from django.utils.timezone import now
from django.conf import settings
from django.shortcuts import redirect
from django.apps import apps  # Importado para buscar modelos dinamicamente
import re

class AuditMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Busca o modelo AuditLog dinamicamente para evitar erros de carregamento
            AuditLog = apps.get_model('app_project', 'AuditLog')  # Substitua 'app_project' pelo nome correto do app
            AuditLog.objects.create(
                user=request.user,
                action='ACCESS',
                description=f"Acesso à URL: {request.path}",
                timestamp=now()  # Adicionado para registro de tempo
            )
        response = self.get_response(request)
        return response


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # URLs que não exigem autenticação
        exempt_urls = [
            settings.LOGIN_URL,
            '/accounts/logout/',
            '/accounts/password_reset/',
            '/accounts/reset/',
            '/',
            '/search/',
            '/register/',
        ]

        # Padrões regex para URLs dinâmicas
        exempt_patterns = [
            r'^/article/\d+/$',  # Padrão para artigos: /article/1/, /article/2/, etc.
        ]

        path = request.path_info
        if not request.user.is_authenticated:
            # Verifica se a URL está na lista de isenções
            if path in exempt_urls:
                return self.get_response(request)

            # Verifica se a URL corresponde a algum padrão regex de isenção
            for pattern in exempt_patterns:
                if re.match(pattern, path):
                    return self.get_response(request)

            # Redireciona para a página de login se não for uma URL isenta
            return redirect(settings.LOGIN_URL)

        return self.get_response(request)
