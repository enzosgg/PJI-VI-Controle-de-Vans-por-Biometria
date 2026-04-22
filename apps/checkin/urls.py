from django .urls import path 
from .import views 

urlpatterns =[


path ('dashboard/',views .dashboard ,name ='dashboard_redirect'),


path ('iniciar-rota/',views .iniciar_rota ,name ='iniciar_rota'),
path ('checkin/<uuid:sessao_id>/',views .checkin_aluno ,name ='checkin_aluno'),
path ('checkout/<uuid:sessao_id>/',views .checkout_escola ,name ='checkout_escola'),
path ('finalizar/<uuid:sessao_id>/',views .finalizar_rota ,name ='finalizar_rota'),
path ('listar-rotas/',views .listar_rotas ,name ='listar_rotas'),


path ('api/capturar-palma/',views .api_capturar_palma ,name ='api_capturar_palma'),
path ('api/sensor-status/',views .api_sensor_status ,name ='api_sensor_status'),
path ('api/ler-biometria/',views .api_ler_biometria ,name ='api_ler_biometria'),
]