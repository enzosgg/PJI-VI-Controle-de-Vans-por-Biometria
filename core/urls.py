from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.login.urls')),
    path('', include('apps.cerebro.urls')),
    path('', include('apps.motorista.urls')),
    path('', include('apps.responsavel.urls')),
    path('', lambda request: redirect('dashboard' if request.user.is_authenticated else 'login')),
    path('ocorrencias/', include('apps.ocorrencias.urls')),
]