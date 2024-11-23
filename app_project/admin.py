from django.contrib import admin
from .models import AuditLog, ArticleAuditLog

# Registrar o modelo AuditLog
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'description', 'timestamp')
    search_fields = ('user__username', 'action', 'description')
    list_filter = ('action', 'timestamp')

admin.site.register(AuditLog, AuditLogAdmin)

# Registrar o modelo ArticleAuditLog
class ArticleAuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'article', 'timestamp', 'details')
    search_fields = ('user__username', 'article__title', 'action')
    list_filter = ('action', 'timestamp')

admin.site.register(ArticleAuditLog, ArticleAuditLogAdmin)
