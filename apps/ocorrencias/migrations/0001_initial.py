

from django .db import migrations ,models 


class Migration (migrations .Migration ):

    initial =True 

    dependencies =[
    ]

    operations =[
    migrations .CreateModel (
    name ='Ocorrencia',
    fields =[
    ('id',models .BigAutoField (auto_created =True ,primary_key =True ,serialize =False ,verbose_name ='ID')),
    ('data_hora',models .DateTimeField (auto_now_add =True )),
    ('tipo',models .CharField (choices =[('ESQUECIMENTO_VAN','Possível Esquecimento dentro da Van'),('ESQUECIMENTO_ESCOLA','Possível Esquecimento na Escola'),('ALERTA_GERAL','Alerta Geral'),('ATRASO','Atraso na Rota'),('PROBLEMA_VAN','Problema com o Veículo'),('OUTRO','Outro')],max_length =20 )),
    ('sessao_rota_id',models .CharField (blank =True ,max_length =100 )),
    ('mensagem',models .TextField ()),
    ('telefone_destino',models .CharField (max_length =20 )),
    ('enviado',models .BooleanField (default =False )),
    ('data_envio',models .DateTimeField (blank =True ,null =True )),
    ],
    ),
    ]
