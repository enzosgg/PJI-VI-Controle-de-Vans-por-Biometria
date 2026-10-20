

import django .db .models .deletion 
from django .db import migrations ,models 


class Migration (migrations .Migration ):

    dependencies =[
    ('cerebro','0005_remove_ocorrencia_rota_ocorrencia_sessao_rota_id'),
    ]

    operations =[
    migrations .RemoveField (
    model_name ='ocorrencia',
    name ='sessao_rota_id',
    ),
    migrations .AddField (
    model_name ='ocorrencia',
    name ='rota',
    field =models .ForeignKey (blank =True ,null =True ,on_delete =django .db .models .deletion .CASCADE ,related_name ='ocorrencias',to ='cerebro.rotas'),
    ),
    ]
