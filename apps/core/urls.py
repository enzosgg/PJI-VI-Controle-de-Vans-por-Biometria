from django .urls import path 
from .import views_admin ,views_motorista ,views_responsavel 
from .views import dashboard 

urlpatterns =[

path ('dashboard/',dashboard ,name ='dashboard'),


path ('admin-dashboard/',views_admin .admin_dashboard ,name ='admin_dashboard'),
path ('admin/usuarios/',views_admin .admin_usuarios_lista ,name ='admin_usuarios_lista'),
path ('admin/usuario/criar/',views_admin .admin_usuario_criar ,name ='admin_usuario_criar'),
path ('admin/usuario/editar/<int:pk>/',views_admin .admin_usuario_editar ,name ='admin_usuario_editar'),
path ('admin/usuario/excluir/<int:pk>/',views_admin .admin_usuario_excluir ,name ='admin_usuario_excluir'),
path ('admin/escolas/',views_admin .admin_escolas_lista ,name ='admin_escolas_lista'),
path ('admin/escola/criar/',views_admin .admin_escola_criar ,name ='admin_escola_criar'),
path ('admin/escola/editar/<int:pk>/',views_admin .admin_escola_editar ,name ='admin_escola_editar'),
path ('admin/escola/excluir/<int:pk>/',views_admin .admin_escola_excluir ,name ='admin_escola_excluir'),
path ('admin/transportes/',views_admin .admin_transportes_lista ,name ='admin_transportes_lista'),
path ('admin/transporte/criar/',views_admin .admin_transporte_criar ,name ='admin_transporte_criar'),
path ('admin/transporte/editar/<int:pk>/',views_admin .admin_transporte_editar ,name ='admin_transporte_editar'),
path ('admin/rotas/',views_admin .admin_rotas_lista ,name ='admin_rotas_lista'),
path ('admin/rota/criar/',views_admin .admin_rota_criar ,name ='admin_rota_criar'),


path ('motorista/dashboard/',views_motorista .motorista_dashboard ,name ='motorista_dashboard'),
path ('motorista/rotas/',views_motorista .motorista_rotas_lista ,name ='motorista_rotas_lista'),
path ('motorista/rota/criar/',views_motorista .motorista_rota_criar ,name ='motorista_rota_criar'),
path ('motorista/lista-padrao/<int:rota_id>/',views_motorista .motorista_lista_padrao ,name ='motorista_lista_padrao'),
path ('motorista/checkin/<int:rota_id>/',views_motorista .motorista_checkin ,name ='motorista_checkin'),
path ('motorista/checkout/<int:rota_id>/',views_motorista .motorista_checkout ,name ='motorista_checkout'),
path ('motorista/verificar-rota/<int:rota_id>/',views_motorista .motorista_verificar_rota ,name ='motorista_verificar_rota'),
path ('motorista/remover-lista/<int:lista_id>/',views_motorista .motorista_remover_lista_padrao ,name ='motorista_remover_lista'),


path ('responsavel/dashboard/',views_responsavel .responsavel_dashboard ,name ='responsavel_dashboard'),
path ('responsavel/aluno/<int:aluno_id>/',views_responsavel .responsavel_aluno_detalhe ,name ='responsavel_aluno_detalhe'),
]