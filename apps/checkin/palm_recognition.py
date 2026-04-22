"""
Versão sem MediaPipe - Usa apenas QR Code e registro manual
"""
import hashlib 
import time 
import json 
import uuid 

class PalmRecognition :
    """Versão sem dependência do MediaPipe - usa QR Code e manual"""

    def __init__ (self ):
        self .available =False 
        print ("Modo simplificado ativado - usando QR Code e registro manual")

    def extract_features (self ,image_data ):
        """
        Retorna um identificador único baseado na imagem
        Como não temos MediaPipe, usamos um ID baseado no timestamp
        """
        import hashlib 


        if isinstance (image_data ,str ):
            hash_data =image_data [:200 ]+str (time .time ())
        else :
            hash_data =str (time .time ())+str (uuid .uuid4 ())

        template_id =hashlib .md5 (hash_data .encode ()).hexdigest ()
        template ={
        'simulated':True ,
        'id':template_id ,
        'timestamp':time .time ()
        }
        return json .dumps (template )

    def compare_templates (self ,template1 ,template2 ,threshold =0.7 ):
        """Comparação simplificada de templates"""
        if not template1 or not template2 :
            return False ,0 

        try :
            t1 =json .loads (template1 )
            t2 =json .loads (template2 )


            if t1 .get ('simulated')and t2 .get ('simulated'):
                return t1 .get ('id')==t2 .get ('id'),1.0 if t1 .get ('id')==t2 .get ('id')else 0.0 

            return False ,0 
        except :
            return False ,0 


palm_recognition =PalmRecognition ()