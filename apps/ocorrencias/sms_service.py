"""
Serviço de envio de SMS - Versão simplificada
"""
import requests 
import json 

class SMSService :
    def __init__ (self ):
        self .provider ='simulado'

    def enviar_sms (self ,telefone ,mensagem ):
        """Envia SMS para o número especificado"""
        print (f"[SMS SIMULADO] Para: {telefone }")
        print (f"Mensagem: {mensagem }")
        print ("-"*50 )
        return True ,"SMS enviado (modo simulado)"

sms_service =SMSService ()