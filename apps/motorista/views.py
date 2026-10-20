from django .shortcuts import render ,redirect ,get_object_or_404 
from django .contrib .auth .decorators import login_required ,user_passes_test 
from django .contrib import messages 
from django .http import JsonResponse 
from django .utils import timezone 
from django .views .decorators .csrf import csrf_exempt 
from apps .cerebro .models import Rotas ,Checkin_Checkout ,Aluno ,Biometria 
from apps .cerebro .palm_recognition import palm_recognition 
import json 

@login_required 
@user_passes_test (lambda u :hasattr (u ,'motorista'),login_url ='dashboard')
def motorista (request ):
    motorista_perfil =request .user .motorista 
    rotas_ativas =Rotas .objects .filter (motorista =motorista_perfil ,status ='ATIVA')
    rotas_finalizadas =Rotas .objects .filter (motorista =motorista_perfil ,status ='FINALIZADA').order_by ('-data_fim')[:10 ]

    context ={
    'rotas_ativas':rotas_ativas ,
    'rotas_finalizadas':rotas_finalizadas ,
    'total_ativas':rotas_ativas .count (),
    }
    return render (request ,'motorista.html',context )

@login_required 
@user_passes_test (lambda u :hasattr (u ,'motorista'),login_url ='dashboard')
def iniciar_rota (request ):
    if request .method =='POST':
        nome_rota =request .POST .get ('nome_rota')
        tipo =request .POST .get ('tipo')
        horario_previsto =request .POST .get ('horario_previsto')


        if not horario_previsto :
            horario_previsto =None 

        sessao =Rotas .objects .create (
        nome_rota =nome_rota ,
        tipo =tipo ,
        motorista =request .user .motorista ,
        horario_previsto =horario_previsto ,
        status ='ATIVA'
        )

        messages .success (request ,f'Rota "{nome_rota }" iniciada com sucesso!')
        return redirect ('checkin_aluno',sessao_id =sessao .id )

    return render (request ,'iniciar_rota.html')

@login_required 
@user_passes_test (lambda u :hasattr (u ,'motorista'),login_url ='dashboard')
def checkin_aluno (request ,sessao_id ):
    sessao =get_object_or_404 (Rotas ,id =sessao_id ,status ='ATIVA')

    if request .method =='POST':
        metodo =request .POST .get ('metodo')
        aluno_id =request .POST .get ('aluno_id')

        aluno =get_object_or_404 (Aluno ,id =aluno_id )

        registro ,created =Checkin_Checkout .objects .get_or_create (
        rota =sessao ,
        aluno =aluno ,
        defaults ={
        'checkin_realizado':True ,
        'horario_checkin':timezone .now (),
        'metodo_checkin':metodo 
        }
        )

        if not created and not registro .checkin_realizado :
            registro .checkin_realizado =True 
            registro .horario_checkin =timezone .now ()
            registro .metodo_checkin =metodo 
            registro .save ()

        messages .success (request ,f'Check-in realizado: {aluno .nome }')
        return redirect ('checkin_aluno',sessao_id =sessao_id )

    registros_queryset =sessao .registros .filter (checkin_realizado =True ).order_by ('horario_checkin')

    context ={
    'sessao':sessao ,
    'registros':registros_queryset ,
    'total_checkins':registros_queryset .count (),

    'alunos_disponiveis':Aluno .objects .all ()
    }
    return render (request ,'checkin_aluno.html',context )

@login_required 
@user_passes_test (lambda u :hasattr (u ,'motorista'),login_url ='dashboard')
def checkout_escola (request ,sessao_id ):
    sessao =get_object_or_404 (Rotas ,id =sessao_id ,status ='ATIVA')

    if request .method =='POST':
        aluno_id =request .POST .get ('aluno_id')

        try :
            registro =sessao .registros .get (aluno_id =aluno_id ,checkin_realizado =True )
            registro .checkout_realizado =True 
            registro .horario_checkout =timezone .now ()
            registro .save ()

            messages .success (request ,f'Check-out realizado: {registro .aluno .nome }')

            divergencia =sessao .get_divergencia ()
            if divergencia >0 :
                messages .warning (request ,f'ATENÇÃO: {divergencia } aluno(s) ainda não fizeram check-out!')

        except Checkin_Checkout .DoesNotExist :
            messages .error (request ,'Aluno não encontrado ou já fez check-out')

        return redirect ('checkout_escola',sessao_id =sessao_id )

    registros_pendentes =sessao .registros .filter (checkin_realizado =True ,checkout_realizado =False ).order_by ('horario_checkin')

    context ={
    'sessao':sessao ,
    'registros':registros_pendentes ,
    'total_checkins':sessao .get_total_checkins (),
    'total_checkouts':sessao .get_total_checkouts (),
    'divergencia':sessao .get_divergencia ()
    }
    return render (request ,'checkout_escola.html',context )

@login_required 
@user_passes_test (lambda u :hasattr (u ,'motorista'),login_url ='dashboard')
def finalizar_rota (request ,sessao_id ):
    sessao =get_object_or_404 (Rotas ,id =sessao_id )

    if request .method =='POST':
        divergencia =sessao .get_divergencia ()
        motivo =request .POST .get ('motivo')

        if divergencia >0 and not motivo :
            mensagem =f"ALERTA GRAVE: Rota {sessao .nome_rota } finalizada com {divergencia } aluno(s) sem check-out!"
            messages .error (request ,mensagem )
            return render (request ,'alerta_esquecimento.html',{
            'sessao':sessao ,
            'divergencia':divergencia 
            })

        sessao .status ='FINALIZADA'
        sessao .data_fim =timezone .now ()
        sessao .save ()

        messages .success (request ,f'Rota "{sessao .nome_rota }" finalizada com sucesso!')
        return redirect ('motorista')

    context ={
    'sessao':sessao ,
    'total_checkins':sessao .get_total_checkins (),
    'total_checkouts':sessao .get_total_checkouts (),
    'divergencia':sessao .get_divergencia ()
    }
    return render (request ,'finalizar_rota.html',context )

@csrf_exempt 
def api_ler_biometria (request ):
    if request .method =='POST':
        try :
            dados =json .loads (request .body )
            template_atual =dados .get ('template')
            sessao_id =dados .get ('sessao_id')

            if not template_atual or not sessao_id :
                return JsonResponse ({'success':False ,'error':'Dados incompletos.'})

            sessao =get_object_or_404 (Rotas ,id =sessao_id )

            alunos_com_biometria =Aluno .objects .filter (biometria__isnull =False )

            for aluno in alunos_com_biometria :
                if aluno .biometria .template_biometrico :
                    match ,score =palm_recognition .comparador_de_palmas (template_atual ,aluno .biometria .template_biometrico )

                    if match :
                        registro ,created =Checkin_Checkout .objects .get_or_create (
                        rota =sessao ,
                        aluno =aluno ,
                        defaults ={
                        'checkin_realizado':True ,
                        'horario_checkin':timezone .now (),
                        'metodo_checkin':'PALMA'
                        }
                        )
                        return JsonResponse ({
                        'success':True ,
                        'aluno_id':aluno .id ,
                        'nome_aluno':aluno .nome 
                        })

            return JsonResponse ({'success':False ,'error':'Aluno não reconhecido.'})

        except Exception as e :
            return JsonResponse ({'success':False ,'error':str (e )})
    return JsonResponse ({'error':'Método não permitido'},status =405 )

@csrf_exempt 
def api_capturar_palma (request ):
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
    return JsonResponse ({
    'ativo':True ,
    'tipo':'palma',
    'mensagem':'Sensor em desenvolvimento',
    'versao_api':'1.0.0'
    })