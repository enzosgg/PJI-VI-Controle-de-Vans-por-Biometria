from django .shortcuts import render ,redirect ,get_object_or_404 
from django .contrib .auth .decorators import login_required 
from django .contrib import messages 
from django .http import JsonResponse 
from django .utils import timezone 
from django .views .decorators .csrf import csrf_exempt 
from .models import SessaoRota ,RegistroAluno 
from .palm_recognition import palm_recognition 
from apps .ocorrencias .views import verificar_esquecimento ,enviar_alertas 
import uuid 
import json 

@login_required 
def dashboard (request ):
    """Dashboard principal do motorista"""
    print ("=== Acessando Dashboard ===")
    print (f"Usuário: {request .user }")

    rotas_ativas =SessaoRota .objects .filter (status ='ATIVA')
    rotas_finalizadas =SessaoRota .objects .filter (status ='FINALIZADA').order_by ('-data_fim')[:10 ]

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
            if template_json :
                registro .palm_template =template_json 
            else :
                messages .error (request ,'Dados biométricos não recebidos do leitor.')
                return redirect ('checkin_aluno',sessao_id =sessao_id )

        registro .checkin_realizado =True 
        registro .horario_checkin =timezone .now ()
        registro .metodo_checkin =metodo 
        registro .save ()

        messages .success (request ,f'Check-in realizado: {nome_aluno }')

        return redirect ('checkin_aluno',sessao_id =sessao_id )

    registros_queryset =sessao .registros .filter (checkin_realizado =True ).order_by ('horario_checkin')

    contador_palma =1 
    registros_processados =[]

    for registro in registros_queryset :
        if registro .metodo_checkin =='PALMA':
            registro .nome_aluno_formatado =f"Aluno {contador_palma }"
            contador_palma +=1 
        else :
            registro .nome_aluno_formatado =registro .nome_aluno 

        registros_processados .append (registro )

    context ={
    'sessao':sessao ,
    'registros':registros_processados ,
    'total_checkins':registros_queryset .count ()
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
                messages .warning (request ,f'ATENÇÃO: {divergencia } aluno(s) ainda não fizeram check-out!')
                verificar_esquecimento (sessao )

        except RegistroAluno .DoesNotExist :
            messages .error (request ,'Aluno não encontrado ou já fez check-out')

        return redirect ('checkout_escola',sessao_id =sessao_id )

    todos_registros_ordenados =sessao .registros .filter (checkin_realizado =True ).order_by ('horario_checkin')

    contador_palma =1 
    registros_pendentes =[]

    for registro in todos_registros_ordenados :
        if registro .metodo_checkin =='PALMA':
            registro .nome_aluno_formatado =f"Aluno {contador_palma }"
            contador_palma +=1 
        else :
            registro .nome_aluno_formatado =registro .nome_aluno 

        if not registro .checkout_realizado :
            registros_pendentes .append (registro )

    context ={
    'sessao':sessao ,
    'registros':registros_pendentes ,
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
        motivo =request .POST .get ('motivo')

        if divergencia >0 and not motivo :
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

        if motivo :
            from apps .ocorrencias .models import Ocorrencia 
            Ocorrencia .objects .create (
            tipo ='DIVERGENCIA_CONFIRMADA',
            sessao_rota_id =str (sessao .id ),
            mensagem =f"Rota finalizada com {divergencia } pendências. Motivo declarado: {motivo }",
            telefone_destino =''
            )

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
    rotas_finalizadas =SessaoRota .objects .filter (status ='FINALIZADA').order_by ('-data_fim')[:20 ]

    context ={
    'rotas_ativas':rotas_ativas ,
    'rotas_finalizadas':rotas_finalizadas 
    }
    return render (request ,'checkin/lista_rotas.html',context )

@login_required 
@csrf_exempt 
def api_capturar_palma (request ):
    """Captura a palma"""
    if request .method =='POST':
        try :
            dados =json .loads (request .body )
            imagem_base64 =dados .get ('imagem')
            if imagem_base64 :
                template_json =palm_recognition .imagem_infos (imagem_base64 )

                if template_json :
                    template_dict =json .loads (template_json )
                    if template_dict .get ("error")=="DORSO_DETECTADO":
                         return JsonResponse ({
                         'success':False ,
                         'error':'Dorso da mão detectado. Por favor, mostre a PALMA da mão virada para a câmera.'
                         })

                    return JsonResponse ({'success':True ,'template':template_json })
                else :
                    return JsonResponse ({'success':False ,'error':'Mão não detectada'})
        except Exception as e :
            return JsonResponse ({'success':False ,'error':str (e )})
    return JsonResponse ({'success':False ,'error':'Método não permitido'})

@csrf_exempt 
def api_sensor_status (request ):
    """Status do sensor"""
    return JsonResponse ({
    'ativo':True ,
    'tipo':'palma',
    'mensagem':'Sensor em desenvolvimento',
    'versao_api':'1.0.0'
    })

@csrf_exempt 
def api_ler_biometria (request ):
    """Leitor de biometria"""
    if request .method =='POST':
        try :
            dados =json .loads (request .body )
            template_atual =dados .get ('template')
            sessao_id =dados .get ('sessao_id')

            if not template_atual or not sessao_id :
                return JsonResponse ({'success':False ,'error':'Dados incompletos.'})

            sessao =get_object_or_404 (SessaoRota ,id =sessao_id )
            alunos_na_van =sessao .registros .filter (checkin_realizado =True ,checkout_realizado =False )

            for registro in alunos_na_van :
                match ,score =palm_recognition .comparador_de_palmas (template_atual ,registro .palm_template )
                if match :
                    return JsonResponse ({
                    'success':True ,
                    'aluno_id':registro .aluno_id_temporario ,
                    'nome_aluno':registro .nome_aluno 
                    })

            return JsonResponse ({'success':False ,'error':'Aluno não reconhecido.'})

        except Exception as e :
            return JsonResponse ({'success':False ,'error':str (e )})
    return JsonResponse ({'error':'Método não permitido'},status =405 )