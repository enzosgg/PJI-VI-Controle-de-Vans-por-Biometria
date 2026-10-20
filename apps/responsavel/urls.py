from django .urls import path 
from .import views 

urlpatterns =[
path ('responsavel/',views .responsavel ,name ='responsavel'),

path ('responsavel/cadastrar-biometria/<int:aluno_id>/',views .cadastrar_biometria ,name ='cadastrar_biometria'),

path ('api/salvar-biometria/',views .api_salvar_biometria ,name ='api_salvar_biometria'),
]