from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

# View temporária para o dashboard
from apps.checkin.views import dashboard

urlpatterns = [
    # Admin do Django
    path('admin/', admin.site.urls),
    
    # Login/Logout
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),

    # Dashboard principal - rota explícita
    path('dashboard/', dashboard, name='dashboard'),
    
    # Redirecionamento da raiz
    path('', lambda request: redirect('dashboard' if request.user.is_authenticated else 'login')),
    
    # Incluir URLs do app checkin (que contém o dashboard)
    path('', include('apps.checkin.urls')),
    
    # Incluir URLs do app ocorrencias
    path('ocorrencias/', include('apps.ocorrencias.urls')),
]