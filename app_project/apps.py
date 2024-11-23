from django.apps import AppConfig


class AppProjectConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_project'

    def ready(self):
        import app_project.signals
