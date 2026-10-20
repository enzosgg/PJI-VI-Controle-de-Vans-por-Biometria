from django .shortcuts import render ,redirect ,get_object_or_404 
from django .contrib .auth .decorators import login_required ,user_passes_test 
from django .http import JsonResponse 
from django .views .decorators .csrf import csrf_exempt 
import json 
from apps .cerebro .models import Aluno ,Biometria 

@login_required 
@user_passes_test (lambda u :hasattr (u ,'responsavel'),login_url ='dashboard')
def responsavel (request ):

    responsavel_perfil =request .user .responsavel 
    alunos =responsavel_perfil .alunos .all ()

    return render (request ,'responsavel.html',{'alunos':alunos })

@login_required 
@user_passes_test (lambda u :hasattr (u ,'responsavel'),login_url ='dashboard')
def cadastrar_biometria (request ,aluno_id ):

    responsavel_perfil =request .user .responsavel 
    aluno =get_object_or_404 (Aluno ,id =aluno_id ,responsavel =responsavel_perfil )

    return render (request ,'cadastrar_biometria.html',{'aluno':aluno })

@csrf_exempt 
@login_required 
def api_salvar_biometria (request ):

    if request .method =='POST':
        try :
            dados =json .loads (request .body )
            aluno_id =dados .get ('aluno_id')
            template =dados .get ('template')

            if not aluno_id or not template :
                return JsonResponse ({'success':False ,'error':'Dados incompletos.'})


            aluno =get_object_or_404 (Aluno ,id =aluno_id ,responsavel =request .user .responsavel )


            biometria ,created =Biometria .objects .get_or_create (aluno =aluno )
            biometria .template_biometrico =template 
            biometria .save ()

            return JsonResponse ({'success':True })

        except Exception as e :
            return JsonResponse ({'success':False ,'error':str (e )})

    return JsonResponse ({'success':False ,'error':'Método inválido.'})