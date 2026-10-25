from django.urls import path
from . import views

urlpatterns = [
    path('responsavel/', views.responsavel, name='responsavel'),
    path('responsavel/cadastrar-biometria/<int:aluno_id>/', views.cadastrar_biometria, name='cadastrar_biometria'),
    path('api/salvar-biometria/', views.api_salvar_biometria, name='api_salvar_biometria'),
    path('responsavel/mapa/<int:aluno_id>/', views.mapa_aluno, name='mapa_aluno'),
    path('api/van/<int:aluno_id>/posicao/', views.api_posicao_van, name='api_posicao_van'),
    path('api/salvar-local/', views.api_salvar_local, name='api_salvar_local'),
    path('api/salvar-avatar/', views.api_salvar_avatar, name='api_salvar_avatar'),
]