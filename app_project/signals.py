from django.db.models.signals import post_save, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import AuditLog

@receiver(post_save, sender=User)
def log_user_changes(sender, instance, created, **kwargs):
    action = 'CREATE' if created else 'UPDATE'
    AuditLog.objects.create(
        user=instance,
        action=action,
        description=f"Usuário {instance.username} foi {'criado' if created else 'atualizado'}."
    )

@receiver(post_delete, sender=User)
def log_user_deletion(sender, instance, **kwargs):
    AuditLog.objects.create(
        user=instance,
        action='DELETE',
        description=f"Usuário {instance.username} foi excluído."
    )

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action='LOGIN',
        description=f"Usuário {user.username} fez login."
    )

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    AuditLog.objects.create(
        user=user,
        action='LOGOUT',
        description=f"Usuário {user.username} fez logout."
    )
