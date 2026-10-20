

from django .db import migrations ,models 


class Migration (migrations .Migration ):

    initial =True 

    dependencies =[
    ]

    operations =[
    migrations .CreateModel (
    name ='Motorista',
    fields =[
    ('id',models .BigAutoField (auto_created =True ,primary_key =True ,serialize =False ,verbose_name ='ID')),
    ('nome',models .CharField (max_length =100 )),
    ],
    ),
    migrations .CreateModel (
    name ='Responsavel',
    fields =[
    ('id',models .BigAutoField (auto_created =True ,primary_key =True ,serialize =False ,verbose_name ='ID')),
    ('nome',models .CharField (max_length =100 )),
    ],
    ),
    ]
