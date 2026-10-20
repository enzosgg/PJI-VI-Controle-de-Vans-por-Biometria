

import django .db .models .deletion 
from django .db import migrations ,models 


class Migration (migrations .Migration ):

    dependencies =[
    ('cerebro','0003_motorista_nome_responsavel_nome_responsavel_telefone_and_more'),
    ]

    operations =[
    migrations .CreateModel (
    name ='Ocorrencia',
    fields =[
    ('id',models .BigAutoField (auto_created =True ,primary_key =True ,serialize =False ,verbose_name ='ID')),
    ('data_hora',models .DateTimeField (auto_now_add =True )),
    ('tipo',models .CharField (choices =[('ESQUECIMENTO_VAN','Possível Esquecimento dentro da Van'),('ESQUECIMENTO_ESCOLA','Possível Esquecimento na Escola'),('ALERTA_GERAL','Alerta Geral'),('ATRASO','Atraso na Rota'),('PROBLEMA_VAN','Problema com o Veículo'),('OUTRO','Outro')],max_length =20 )),
    ('mensagem',models .TextField ()),
    ('telefone_destino',models .CharField (max_length =20 )),
    ('enviado',models .BooleanField (default =False )),
    ('data_envio',models .DateTimeField (blank =True ,null =True )),
    ('rota',models .ForeignKey (blank =True ,null =True ,on_delete =django .db .models .deletion .CASCADE ,related_name ='ocorrencias',to ='cerebro.rotas')),
    ],
    ),
    ]
