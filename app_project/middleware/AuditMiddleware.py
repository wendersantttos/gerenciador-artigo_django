import logging
from django.utils.timezone import make_aware
from django.contrib.auth.models import User
from datetime import datetime
from app_project.models import AuditLog

class AuditMiddleware:
    """
    Middleware que cria logs de auditoria para ações dos usuários.
    Registra acessos, login, logout, criação, atualização e exclusão de objetos.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Processa a requisição antes de continuar
        self.process_request(request)

        # Processa a resposta
        response = self.get_response(request)

        # Processa após a resposta ser gerada
        self.process_response(request, response)

        return response

    def process_request(self, request):
        """
        Registra eventos como login, logout ou acesso a uma URL.
        """
        user = request.user if request.user.is_authenticated else None
        if user:
            # Registra acessos à página
            self.create_audit_log(user, 'ACCESS', f'User accessed {request.path}')

    def process_response(self, request, response):
        """
        Registra ações específicas após a resposta, como criação, atualização ou exclusão de objetos.
        """
        user = request.user if request.user.is_authenticated else None

        # Verifica se foi uma ação de POST ou DELETE que pode modificar objetos
        if user and request.method in ['POST', 'DELETE']:
            self.handle_create_update_delete(request, user)

        return response

    def handle_create_update_delete(self, request, user):
        """
        Registra criação, atualização ou exclusão de objetos.
        """
        action = None
        description = ""
        
        # Exemplo de registro para criação
        if request.method == 'POST' and 'create' in request.POST:
            action = 'CREATE'
            description = f'User created an object at {request.path}'
        
        # Exemplo de registro para exclusão
        elif request.method == 'DELETE' and 'delete' in request.GET:
            action = 'DELETE'
            description = f'User deleted an object at {request.path}'

        if action:
            self.create_audit_log(user, action, description)

    def create_audit_log(self, user, action, description):
        """
        Cria um log de auditoria no banco de dados.
        """
        timestamp = make_aware(datetime.now())  # Garante o horário ciente de fuso horário
        # Criação do log de auditoria
        AuditLog.objects.create(
            user=user,
            action=action,
            description=description,
            timestamp=timestamp
        )
