from django .db import models 
from datetime import datetime 

class Ocorrencia (models .Model ):
    TIPOS =(
    ('ESQUECIMENTO_VAN','Possível Esquecimento dentro da Van'),
    ('ESQUECIMENTO_ESCOLA','Possível Esquecimento na Escola'),
    ('ALERTA_GERAL','Alerta Geral'),
    ('ATRASO','Atraso na Rota'),
    ('PROBLEMA_VAN','Problema com o Veículo'),
    ('OUTRO','Outro'),
    )

    data_hora =models .DateTimeField (auto_now_add =True )
    tipo =models .CharField (max_length =20 ,choices =TIPOS )
    sessao_rota_id =models .CharField (max_length =100 ,blank =True )
    mensagem =models .TextField ()
    telefone_destino =models .CharField (max_length =20 )
    enviado =models .BooleanField (default =False )
    data_envio =models .DateTimeField (null =True ,blank =True )

    def __str__ (self ):
        return f"{self .data_hora .strftime ('%d/%m/%Y %H:%M')} - {self .get_tipo_display ()}"