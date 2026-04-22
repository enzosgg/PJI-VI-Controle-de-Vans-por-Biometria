from django .urls import path 
from .import views 

urlpatterns =[
path ('criar/',views .criar_ocorrencia ,name ='criar_ocorrencia'),
path ('lista/',views .lista_ocorrencias ,name ='lista_ocorrencias'),
]