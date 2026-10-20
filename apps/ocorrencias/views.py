from django .shortcuts import render ,redirect 
from django .contrib .auth .decorators import login_required 
from django .contrib import messages 
from django .utils import timezone 
from apps .cerebro .models import Ocorrencia ,Rotas 
import os 
import json 
from datetime import datetime 

def verificar_esquecimento (sessao ):
    """Verifica se há esquecimento na rota"""
    divergencia =sessao .get_divergencia ()

    if divergencia >0 :
        mensagem =f"ALERTA: {divergencia } aluno(s) sem check-out na rota {sessao .nome_rota }"

        ocorrencia =Ocorrencia .objects .create (
        tipo ='ESQUECIMENTO_VAN'if sessao .tipo =='IDA'else 'ESQUECIMENTO_ESCOLA',
        rota =sessao ,
        mensagem =mensagem ,
        telefone_destino =''
        )

        return ocorrencia 
    return None 

def enviar_alertas (sessao ,mensagem ):
    """Envia alertas via SMS e salva em arquivo"""

    log_file ='logs/ocorrencias.txt'
    os .makedirs ('logs',exist_ok =True )

    with open (log_file ,'a',encoding ='utf-8')as f :
        log_entry ={
        'data':datetime .now ().strftime ('%d/%m/%Y %H:%M:%S'),
        'rota':sessao .nome_rota ,
        'motorista':sessao .motorista .nome if sessao .motorista else 'Desconhecido',
        'mensagem':mensagem ,
        'divergencia':sessao .get_divergencia ()
        }
        f .write (json .dumps (log_entry ,ensure_ascii =False )+'\n')

    enviar_sms (sessao ,mensagem )

def enviar_sms (sessao ,mensagem ):
    """Envia SMS para os responsáveis (simulado)"""
    registros =sessao .registros .filter (checkin_realizado =True ,checkout_realizado =False )

    for registro in registros :
        if registro .aluno and registro .aluno .responsavel and registro .aluno .responsavel .telefone :
            print (f"[SMS SIMULADO] Para: {registro .aluno .responsavel .telefone }")
            print (f"Mensagem: {mensagem } - Aluno: {registro .aluno .nome }")
            print ("-"*50 )

@login_required 
def criar_ocorrencia (request ):
    """Cria uma nova ocorrência manual"""
    if request .method =='POST':
        tipo =request .POST .get ('tipo')
        mensagem =request .POST .get ('mensagem')
        telefone =request .POST .get ('telefone')

        ocorrencia =Ocorrencia .objects .create (
        tipo =tipo ,
        mensagem =mensagem ,
        telefone_destino =telefone 
        )

        log_file ='logs/ocorrencias.txt'
        os .makedirs ('logs',exist_ok =True )

        with open (log_file ,'a',encoding ='utf-8')as f :
            log_entry ={
            'data':datetime .now ().strftime ('%d/%m/%Y %H:%M:%S'),
            'tipo':tipo ,
            'mensagem':mensagem ,
            'telefone':telefone ,
            'motorista':request .user .motorista .nome if hasattr (request .user ,'motorista')else request .user .username 
            }
            f .write (json .dumps (log_entry ,ensure_ascii =False )+'\n')

        messages .success (request ,'Ocorrência registrada com sucesso!')
        return redirect ('lista_ocorrencias')


    return render (request ,'criar_ocorrencia.html')

@login_required 
def lista_ocorrencias (request ):
    ocorrencias =Ocorrencia .objects .all ().order_by ('-data_hora')[:50 ]

    return render (request ,'lista_ocorrencias.html',{'ocorrencias':ocorrencias })