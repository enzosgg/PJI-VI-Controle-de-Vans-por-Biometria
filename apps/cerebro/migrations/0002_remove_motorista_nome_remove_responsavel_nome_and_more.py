

import django .db .models .deletion 
from django .conf import settings 
from django .db import migrations ,models 


class Migration (migrations .Migration ):

    dependencies =[
    ('cerebro','0001_initial'),
    migrations .swappable_dependency (settings .AUTH_USER_MODEL ),
    ]

    operations =[
    migrations .RemoveField (
    model_name ='motorista',
    name ='nome',
    ),
    migrations .RemoveField (
    model_name ='responsavel',
    name ='nome',
    ),
    migrations .AddField (
    model_name ='motorista',
    name ='user',
    field =models .OneToOneField (blank =True ,null =True ,on_delete =django .db .models .deletion .CASCADE ,related_name ='motorista',to =settings .AUTH_USER_MODEL ),
    ),
    migrations .AddField (
    model_name ='responsavel',
    name ='user',
    field =models .OneToOneField (blank =True ,null =True ,on_delete =django .db .models .deletion .CASCADE ,related_name ='responsavel',to =settings .AUTH_USER_MODEL ),
    ),
    ]
