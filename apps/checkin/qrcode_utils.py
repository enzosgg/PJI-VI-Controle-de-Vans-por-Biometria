"""
Utilitários para geração e leitura de QR Code
Versão simplificada
"""
import qrcode 
import uuid 
from io import BytesIO 
import base64 
import json 

class QRCodeUtils :
    """Utilitários para QR Code"""

    @staticmethod 
    def gerar_qrcode (aluno_id_temporario ,dados_adicionais =None ):
        """Gera um QR Code para o aluno"""
        dados ={
        'id':aluno_id_temporario ,
        'timestamp':str (uuid .uuid4 ()),
        'type':'checkin_aluno'
        }

        if dados_adicionais :
            dados .update (dados_adicionais )

        dados_str =json .dumps (dados )

        qr =qrcode .QRCode (
        version =1 ,
        error_correction =qrcode .constants .ERROR_CORRECT_L ,
        box_size =10 ,
        border =4 ,
        )
        qr .add_data (dados_str )
        qr .make (fit =True )

        img =qr .make_image (fill_color ="black",back_color ="white")

        buffer =BytesIO ()
        img .save (buffer ,format ="PNG")
        img_base64 =base64 .b64encode (buffer .getvalue ()).decode ()

        return f"data:image/png;base64,{img_base64 }"

    @staticmethod 
    def ler_qrcode (imagem_base64 ):
        """Lê um QR Code a partir de uma imagem base64 (simulado)"""
        try :
            if 'base64,'in imagem_base64 :
                imagem_base64 =imagem_base64 .split ('base64,')[1 ]


            return {'id':'simulado_'+str (uuid .uuid4 ())[:8 ]}

        except Exception as e :
            print (f"Erro ao ler QR Code: {e }")
            return None 

qrcode_utils =QRCodeUtils ()