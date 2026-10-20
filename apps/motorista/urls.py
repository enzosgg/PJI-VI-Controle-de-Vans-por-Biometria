from django .urls import path 
from .import views 

urlpatterns =[

path ('motorista/',views .motorista ,name ='motorista'),


path ('motorista/iniciar-rota/',views .iniciar_rota ,name ='iniciar_rota'),
path ('motorista/checkin/<uuid:sessao_id>/',views .checkin_aluno ,name ='checkin_aluno'),
path ('motorista/checkout/<uuid:sessao_id>/',views .checkout_escola ,name ='checkout_escola'),
path ('motorista/finalizar/<uuid:sessao_id>/',views .finalizar_rota ,name ='finalizar_rota'),


path ('api/capturar-palma/',views .api_capturar_palma ,name ='api_capturar_palma'),
path ('api/sensor-status/',views .api_sensor_status ,name ='api_sensor_status'),
path ('api/ler-biometria/',views .api_ler_biometria ,name ='api_ler_biometria'),


]