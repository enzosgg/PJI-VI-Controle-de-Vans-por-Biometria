

import django .db .models .deletion 
import uuid 
from django .db import migrations ,models 


class Migration (migrations .Migration ):

    dependencies =[
    ('cerebro','0002_remove_motorista_nome_remove_responsavel_nome_and_more'),
    ]

    operations =[
    migrations .AddField (
    model_name ='motorista',
    name ='nome',
    field =models .CharField (default ='Sem nome',max_length =100 ),
    ),
    migrations .AddField (
    model_name ='responsavel',
    name ='nome',
    field =models .CharField (default ='Sem nome',max_length =100 ),
    ),
    migrations .AddField (
    model_name ='responsavel',
    name ='telefone',
    field =models .CharField (blank =True ,max_length =20 ),
    ),
    migrations .CreateModel (
    name ='Aluno',
    fields =[
    ('id',models .BigAutoField (auto_created =True ,primary_key =True ,serialize =False ,verbose_name ='ID')),
    ('nome',models .CharField (max_length =100 )),
    ('responsavel',models .ForeignKey (on_delete =django .db .models .deletion .CASCADE ,related_name ='alunos',to ='cerebro.responsavel')),
    ],
    ),
    migrations .CreateModel (
    name ='Biometria',
    fields =[
    ('id',models .BigAutoField (auto_created =True ,primary_key =True ,serialize =False ,verbose_name ='ID')),
    ('template_biometrico',models .TextField (blank =True )),
    ('aluno',models .OneToOneField (on_delete =django .db .models .deletion .CASCADE ,related_name ='biometria',to ='cerebro.aluno')),
    ],
    ),
    migrations .CreateModel (
    name ='Rotas',
    fields =[
    ('id',models .UUIDField (default =uuid .uuid4 ,editable =False ,primary_key =True ,serialize =False )),
    ('nome_rota',models .CharField (help_text ='Ex: Rota Manhã - Bairro A',max_length =100 )),
    ('tipo',models .CharField (choices =[('IDA','Ida para Escola'),('VOLTA','Volta para Casa')],max_length =5 )),
    ('data_inicio',models .DateTimeField (auto_now_add =True )),
    ('data_fim',models .DateTimeField (blank =True ,null =True )),
    ('status',models .CharField (choices =[('ATIVA','Ativa'),('FINALIZADA','Finalizada'),('CANCELADA','Cancelada')],default ='ATIVA',max_length =10 )),
    ('horario_previsto',models .TimeField (blank =True ,null =True )),
    ('motorista',models .ForeignKey (null =True ,on_delete =django .db .models .deletion .CASCADE ,related_name ='rotas_realizadas',to ='cerebro.motorista')),
    ],
    ),
    migrations .CreateModel (
    name ='Checkin_Checkout',
    fields =[
    ('id',models .BigAutoField (auto_created =True ,primary_key =True ,serialize =False ,verbose_name ='ID')),
    ('checkin_realizado',models .BooleanField (default =False )),
    ('checkout_realizado',models .BooleanField (default =False )),
    ('horario_checkin',models .DateTimeField (blank =True ,null =True )),
    ('horario_checkout',models .DateTimeField (blank =True ,null =True )),
    ('metodo_checkin',models .CharField (blank =True ,max_length =20 )),
    ('observacao',models .TextField (blank =True )),
    ('aluno',models .ForeignKey (null =True ,on_delete =django .db .models .deletion .CASCADE ,related_name ='historico_viagens',to ='cerebro.aluno')),
    ('rota',models .ForeignKey (null =True ,on_delete =django .db .models .deletion .CASCADE ,related_name ='registros',to ='cerebro.rotas')),
    ],
    ),
    migrations .AddField (
    model_name ='aluno',
    name ='rota',
    field =models .ForeignKey (blank =True ,null =True ,on_delete =django .db .models .deletion .SET_NULL ,related_name ='alunos',to ='cerebro.rotas'),
    ),
    ]
