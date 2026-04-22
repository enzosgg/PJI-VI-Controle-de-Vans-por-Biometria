

import django .db .models .deletion 
import uuid 
from django .db import migrations ,models 


class Migration (migrations .Migration ):

    initial =True 

    dependencies =[
    ]

    operations =[
    migrations .CreateModel (
    name ='SessaoRota',
    fields =[
    ('id',models .UUIDField (default =uuid .uuid4 ,editable =False ,primary_key =True ,serialize =False )),
    ('nome_rota',models .CharField (help_text ='Ex: Rota Manhã - Bairro A',max_length =100 )),
    ('tipo',models .CharField (choices =[('IDA','Ida para Escola'),('VOLTA','Volta para Casa')],max_length =5 )),
    ('data_inicio',models .DateTimeField (auto_now_add =True )),
    ('data_fim',models .DateTimeField (blank =True ,null =True )),
    ('status',models .CharField (choices =[('ATIVA','Ativa'),('FINALIZADA','Finalizada'),('CANCELADA','Cancelada')],default ='ATIVA',max_length =10 )),
    ('motorista',models .CharField (blank =True ,default ='',max_length =100 )),
    ('horario_previsto',models .TimeField (blank =True ,null =True )),
    ],
    ),
    migrations .CreateModel (
    name ='RegistroAluno',
    fields =[
    ('id',models .UUIDField (default =uuid .uuid4 ,editable =False ,primary_key =True ,serialize =False )),
    ('aluno_id_temporario',models .CharField (max_length =50 )),
    ('nome_aluno',models .CharField (blank =True ,max_length =200 )),
    ('responsavel',models .CharField (blank =True ,max_length =200 )),
    ('telefone_responsavel',models .CharField (blank =True ,max_length =20 )),
    ('palm_template',models .TextField (blank =True )),
    ('qrcode_data',models .CharField (blank =True ,max_length =200 )),
    ('checkin_realizado',models .BooleanField (default =False )),
    ('checkout_realizado',models .BooleanField (default =False )),
    ('horario_checkin',models .DateTimeField (blank =True ,null =True )),
    ('horario_checkout',models .DateTimeField (blank =True ,null =True )),
    ('metodo_checkin',models .CharField (blank =True ,max_length =20 )),
    ('observacao',models .TextField (blank =True )),
    ('sessao_rota',models .ForeignKey (on_delete =django .db .models .deletion .CASCADE ,related_name ='registros',to ='checkin.sessaorota')),
    ],
    options ={
    'unique_together':{('sessao_rota','aluno_id_temporario')},
    },
    ),
    ]
