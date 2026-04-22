import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.urls import get_resolver

def listar_urls():
    resolver = get_resolver()
    urls = []
    
    def collect_urls(patterns, prefix=''):
        for pattern in patterns:
            if hasattr(pattern, 'url_patterns'):
                collect_urls(pattern.url_patterns, prefix + str(pattern.pattern))
            else:
                urls.append(prefix + str(pattern.pattern))
    
    collect_urls(resolver.url_patterns)
    
    print("=== URLs Disponíveis ===\n")
    for url in sorted(urls):
        print(url)
    
    print("\n=== URLs por nome ===\n")
    from django.urls import reverse
    try:
        print(f"dashboard: {reverse('dashboard')}")
    except:
        print("dashboard: NÃO ENCONTRADA")
    
    try:
        print(f"listar_rotas: {reverse('listar_rotas')}")
    except:
        print("listar_rotas: NÃO ENCONTRADA")

if __name__ == '__main__':
    listar_urls()