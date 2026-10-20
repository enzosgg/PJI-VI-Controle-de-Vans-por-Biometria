

from django .db import migrations ,models 


class Migration (migrations .Migration ):

    dependencies =[
    ('cerebro','0004_ocorrencia'),
    ]

    operations =[
    migrations .RemoveField (
    model_name ='ocorrencia',
    name ='rota',
    ),
    migrations .AddField (
    model_name ='ocorrencia',
    name ='sessao_rota_id',
    field =models .CharField (blank =True ,max_length =100 ),
    ),
    ]
