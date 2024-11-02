from django.contrib import admin
from .models import CustomUser, Article, ArticleHistory, AuditLog

admin.site.register(CustomUser)
admin.site.register(Article)
admin.site.register(ArticleHistory)
admin.site.register(AuditLog)
