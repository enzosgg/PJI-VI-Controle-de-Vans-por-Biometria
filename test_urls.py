import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import reverse, resolve

print("=== Teste de URLs ===\n")

# Testar URLs
urls_to_test = [
    'dashboard',
    'iniciar_rota',
    'listar_rotas',
    'login',
    'logout',
]

for url_name in urls_to_test:
    try:
        url = reverse(url_name)
        resolver = resolve(url)
        print(f"✓ {url_name}: {url} -> {resolver.func.__name__}")
    except Exception as e:
        print(f"✗ {url_name}: ERRO - {e}")

print("\n=== URLs disponíveis ===")
from django.urls import get_resolver

resolver = get_resolver()
for pattern in resolver.url_patterns:
    print(f"  {pattern}")