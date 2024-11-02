from django.db import models
from django.core.validators import (
    RegexValidator, MinLengthValidator, MaxLengthValidator,
    MinValueValidator, MaxValueValidator, FileExtensionValidator
)
from django.contrib.auth.models import AbstractUser, Group, Permission
from rest_framework import serializers
import datetime


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student')
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    # Atualizar related_name para evitar conflitos
    groups = models.ManyToManyField(Group, related_name='customuser_set', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_permissions_set', blank=True)

    def __str__(self):
        return self.username


class Article(models.Model):
    title = models.CharField(max_length=200, validators=[MinLengthValidator(10)])
    authors = models.CharField(max_length=500)
    abstract = models.TextField(validators=[
        MinLengthValidator(100),
        MaxLengthValidator(1500)
    ])
    keywords = models.CharField(max_length=400, validators=[
        RegexValidator(
            regex=r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]+(\.\s*[A-Za-zÀ-ÖØ-öø-ÿ\s]+)*\.$',
            message='As palavras-chave devem ser frases separadas por ponto e espaço (ex: "Frase 1. Frase 2.").'
        )
    ])
    date = models.IntegerField(validators=[
        MinValueValidator(1900),
        MaxValueValidator(datetime.datetime.now().year)
    ])
    journal = models.CharField(max_length=200, blank=True, null=True)  # Campo opcional
    pdf_file = models.FileField(upload_to='articles/pdfs/', validators=[
        FileExtensionValidator(allowed_extensions=['pdf'])
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_articles")
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_articles")

    def __str__(self):
        return self.title


class ArticleHistory(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='history')
    title = models.CharField(max_length=200)
    authors = models.CharField(max_length=500)
    abstract = models.TextField()
    keywords = models.CharField(max_length=400)
    updated_at = models.DateTimeField(auto_now_add=True)  # Quando essa versão foi criada

    def __str__(self):
        return f"Versão de {self.updated_at.strftime('%d/%m/%Y %H:%M')} do artigo '{self.article.title}'"


# Model for audit log entries
class AuditLog(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)  # Ex: "created", "updated", "deleted"
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs")
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)  # Detalhes adicionais da ação, como mudanças feitas

    def __str__(self):
        return f"{self.user} {self.action} em {self.article} em {self.timestamp.strftime('%d/%m/%Y %H:%M')}"


# Serializer for Article model with date validation
class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = [
            'id', 'title', 'authors', 'abstract', 
            'keywords', 'date', 'journal', 'pdf_file', 
            'created_at', 'updated_at', 'created_by', 'updated_by'
        ]

    def validate_date(self, value):
        """Garantir que a data não está no futuro."""
        if value > datetime.datetime.now().year:
            raise serializers.ValidationError("A data não pode estar no futuro.")
        return value
