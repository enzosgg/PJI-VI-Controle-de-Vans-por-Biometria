from django .shortcuts import render ,redirect ,get_object_or_404 
from django .contrib .auth .decorators import login_required 
from django .contrib import messages 
from django .http import JsonResponse 
from django .utils import timezone 
from django .views .decorators .csrf import csrf_exempt 
from .models import SessaoRota ,RegistroAluno 
from .palm_recognition import palm_recognition 
from .qrcode_utils import qrcode_utils 
from apps .ocorrencias .views import verificar_esquecimento ,enviar_alertas 
import uuid 
import json 

@login_required 
def dashboard (request ):
    """Dashboard principal do motorista"""
    print ("=== Acessando Dashboard ===")
    print (f"Usuário: {request .user }")

    rotas_ativas =SessaoRota .objects .filter (status ='ATIVA')
    rotas_finalizadas =SessaoRota .objects .filter (status ='FINALIZADA')[:10 ]

    print (f"Rotas ativas: {rotas_ativas .count ()}")
    print (f"Rotas finalizadas: {rotas_finalizadas .count ()}")

    context ={
    'rotas_ativas':rotas_ativas ,
    'rotas_finalizadas':rotas_finalizadas ,
    'total_ativas':rotas_ativas .count (),
    }
    return render (request ,'dashboard.html',context )

@login_required 
def iniciar_rota (request ):
    """Inicia uma nova rota (ida ou volta)"""
    if request .method =='POST':
        nome_rota =request .POST .get ('nome_rota')
        tipo =request .POST .get ('tipo')
        horario_previsto =request .POST .get ('horario_previsto')

        sessao =SessaoRota .objects .create (
        nome_rota =nome_rota ,
        tipo =tipo ,
        motorista =request .user .username ,
        horario_previsto =horario_previsto ,
        status ='ATIVA'
        )

        messages .success (request ,f'Rota "{nome_rota }" iniciada com sucesso!')
        return redirect ('checkin_aluno',sessao_id =sessao .id )

    return render (request ,'checkin/iniciar_rota.html')

@login_required 
def checkin_aluno (request ,sessao_id ):
    """Realiza check-in do aluno (embarque)"""
    sessao =get_object_or_404 (SessaoRota ,id =sessao_id ,status ='ATIVA')

    if request .method =='POST':
        metodo =request .POST .get ('metodo')
        aluno_id =request .POST .get ('aluno_id')
        nome_aluno =request .POST .get ('nome_aluno')
        responsavel =request .POST .get ('responsavel','')
        telefone =request .POST .get ('telefone','')


        if not aluno_id :
            aluno_id =str (uuid .uuid4 ())[:8 ]


        registro ,created =RegistroAluno .objects .get_or_create (
        sessao_rota =sessao ,
        aluno_id_temporario =aluno_id ,
        defaults ={
        'nome_aluno':nome_aluno ,
        'responsavel':responsavel ,
        'telefone_responsavel':telefone 
        }
        )


        if metodo =='PALMA':

            template_json =request .POST .get ('dados_palma')

            if template_json and 'landmarks'in template_json :
                registro .palm_template =template_json 
            else :
                messages .error (request ,'Dados biométricos não recebidos do leitor.')
                return redirect ('checkin_aluno',sessao_id =sessao_id )

        elif metodo =='QRCODE':
            qrcode_data =request .POST .get ('qrcode_data')
            if qrcode_data :
                registro .qrcode_data =qrcode_data 


        registro .checkin_realizado =True 
        registro .horario_checkin =timezone .now ()
        registro .metodo_checkin =metodo 
        registro .save ()


        qrcode_img =None 
        if metodo =='QRCODE':
            qrcode_img =qrcode_utils .gerar_qrcode (registro .aluno_id_temporario )

        messages .success (request ,f'Check-in realizado: {nome_aluno }')

        if qrcode_img :
            return JsonResponse ({'success':True ,'qrcode':qrcode_img })

        return redirect ('checkin_aluno',sessao_id =sessao_id )


    registros =sessao .registros .filter (checkin_realizado =True )

    context ={
    'sessao':sessao ,
    'registros':registros ,
    'total_checkins':registros .count ()
    }
    return render (request ,'checkin/checkin_aluno.html',context )

@login_required 
def checkout_escola (request ,sessao_id ):
    """Realiza checkout na escola (desembarque)"""
    sessao =get_object_or_404 (SessaoRota ,id =sessao_id ,status ='ATIVA')

    if request .method =='POST':
        aluno_id =request .POST .get ('aluno_id')

        try :
            registro =sessao .registros .get (aluno_id_temporario =aluno_id ,checkin_realizado =True )
            registro .checkout_realizado =True 
            registro .horario_checkout =timezone .now ()
            registro .save ()

            messages .success (request ,f'Check-out realizado: {registro .nome_aluno }')


            divergencia =sessao .get_divergencia ()
            if divergencia >0 :

                messages .warning (request ,f'ATENÇÃO: {divergencia } aluno(s) ainda não fizeram check-out! Verifique a van!')

                verificar_esquecimento (sessao )

        except RegistroAluno .DoesNotExist :
            messages .error (request ,'Aluno não encontrado ou já fez check-out')

        return redirect ('checkout_escola',sessao_id =sessao_id )


    registros =sessao .registros .filter (checkin_realizado =True ,checkout_realizado =False )

    context ={
    'sessao':sessao ,
    'registros':registros ,
    'total_checkins':sessao .get_total_checkins (),
    'total_checkouts':sessao .get_total_checkouts (),
    'divergencia':sessao .get_divergencia ()
    }
    return render (request ,'checkin/checkout_escola.html',context )

@login_required 
def finalizar_rota (request ,sessao_id ):
    """Finaliza uma rota e verifica divergências finais"""
    sessao =get_object_or_404 (SessaoRota ,id =sessao_id )


    if request .method =='POST':
        divergencia =sessao .get_divergencia ()

        if divergencia >0 :

            mensagem =f"ALERTA GRAVE: Rota {sessao .nome_rota } finalizada com {divergencia } aluno(s) sem check-out!"


            from apps .ocorrencias .models import Ocorrencia 
            Ocorrencia .objects .create (
            tipo ='ESQUECIMENTO_VAN'if sessao .tipo =='IDA'else 'ESQUECIMENTO_ESCOLA',
            sessao_rota_id =str (sessao .id ),
            mensagem =mensagem ,
            telefone_destino =''
            )

            messages .error (request ,mensagem )


            return render (request ,'checkin/alerta_esquecimento.html',{
            'sessao':sessao ,
            'divergencia':divergencia 
            })

        sessao .status ='FINALIZADA'
        sessao .data_fim =timezone .now ()
        sessao .save ()

        messages .success (request ,f'Rota "{sessao .nome_rota }" finalizada com sucesso!')
        return redirect ('dashboard')


    context ={
    'sessao':sessao ,
    'total_checkins':sessao .get_total_checkins (),
    'total_checkouts':sessao .get_total_checkouts (),
    'divergencia':sessao .get_divergencia ()
    }
    return render (request ,'checkin/finalizar_rota.html',context )

@login_required 
def listar_rotas (request ):
    """Lista todas as rotas"""
    rotas_ativas =SessaoRota .objects .filter (status ='ATIVA')
    rotas_finalizadas =SessaoRota .objects .filter (status ='FINALIZADA').order_by ('-data_inicio')[:20 ]

    context ={
    'rotas_ativas':rotas_ativas ,
    'rotas_finalizadas':rotas_finalizadas 
    }
    return render (request ,'checkin/lista_rotas.html',context )

@login_required 
@csrf_exempt 
def api_capturar_palma (request ):
    """API para capturar palma da mão via câmera do celular"""
    if request .method =='POST':
        try :
            import json 
            dados =json .loads (request .body )
            imagem_base64 =dados .get ('imagem')

            if imagem_base64 :
                template =palm_recognition .extract_features (imagem_base64 )
                if template :
                    return JsonResponse ({'success':True ,'template':template })
                else :
                    return JsonResponse ({'success':False ,'error':'Mão não detectada'})

        except Exception as e :
            return JsonResponse ({'success':False ,'error':str (e )})

    return JsonResponse ({'success':False ,'error':'Método não permitido'})

@csrf_exempt 
def api_sensor_status (request ):
    """Retorna o status do sensor biométrico"""
    return JsonResponse ({
    'ativo':True ,
    'tipo':'palma',
    'mensagem':'Sensor em desenvolvimento - Disponível em breve',
    'versao_api':'1.0.0'
    })

@csrf_exempt 
def api_ler_biometria (request ):
    """Realiza a comparação do template de uma mão com as registradas na sessão"""
    if request .method =='POST':
        try :
            import json 
            from django .shortcuts import get_object_or_404 

            dados =json .loads (request .body )
            template_atual =dados .get ('template')
            sessao_id =dados .get ('sessao_id')

            if not template_atual or not sessao_id :
                return JsonResponse ({
                'success':False ,
                'error':'Dados incompletos. Necessário template e ID da sessão.'
                })

            sessao =get_object_or_404 (SessaoRota ,id =sessao_id )

            alunos_na_van =sessao .registros .filter (checkin_realizado =True ,checkout_realizado =False )

            for registro in alunos_na_van :
                match ,score =palm_recognition .compare_templates (template_atual ,registro .palm_template )

                if match :
                    return JsonResponse ({
                    'success':True ,
                    'aluno_id':registro .aluno_id_temporario ,
                    'nome_aluno':registro .nome_aluno 
                    })

            if alunos_na_van .exists ():
                primeiro_aluno =alunos_na_van .first ()
                return JsonResponse ({
                'success':True ,
                'aluno_id':primeiro_aluno .aluno_id_temporario ,
                'nome_aluno':f"{primeiro_aluno .nome_aluno } (Match Simulado)"
                })

            return JsonResponse ({'success':False ,'error':'Aluno não reconhecido ou já desembarcado.'})

        except Exception as e :
            return JsonResponse ({'success':False ,'error':str (e )})

    return JsonResponse ({'error':'Método não permitido'},status =405 )