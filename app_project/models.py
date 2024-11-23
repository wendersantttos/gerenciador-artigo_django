from django.db import models
from django.core.validators import (
    RegexValidator, MinLengthValidator, MaxLengthValidator,
    MinValueValidator, MaxValueValidator, FileExtensionValidator
)
from django.contrib.auth.models import User
from django.utils.timezone import now
import datetime


def validate_pdf_size(value):
    """ Valida o tamanho do arquivo PDF. O tamanho máximo é 10MB. """
    filesize = value.size  # Tamanho do arquivo em bytes
    limit = 10 * 1024 * 1024  # Limite de 10MB

    if filesize > limit:
        raise ValidationError(f"O arquivo não pode ser maior que 10MB. Tamanho atual: {filesize / (1024 * 1024):.2f} MB.")


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('CREATE', 'Criação'),
        ('UPDATE', 'Atualização'),
        ('DELETE', 'Exclusão'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('ACCESS', 'Acesso'),
        ('DELETION', 'Exclusão de Dados'),
        ('OTHER', 'Outro'),  # Exemplo de possível valor maior
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100, choices=ACTION_CHOICES)  # Aumente o tamanho para 100 ou mais
    description = models.TextField(default="Ação realizada no sistema.", null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.action} - {self.timestamp}"



class Article(models.Model):
    title = models.CharField(max_length=300, validators=[MinLengthValidator(10)])
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
    journal = models.CharField(max_length=200, blank=True, null=True)
    pdf_file = models.FileField(upload_to='articles/pdfs/', validators=[
        FileExtensionValidator(allowed_extensions=['pdf']),
        validate_pdf_size  # Função de validação personalizada para tamanho do arquivo
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="created_articles")
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name="updated_articles")

    def __str__(self):
        return self.title


class ArticleHistory(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='history')
    title = models.CharField(max_length=200)
    authors = models.CharField(max_length=500)
    abstract = models.TextField()
    keywords = models.CharField(max_length=400)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Versão de {self.updated_at.strftime('%d/%m/%Y %H:%M')} do artigo '{self.article.title}'"


class ArticleAuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=200)  # Tamanho maior para descrever melhor as ações
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs")
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} {self.action} no artigo '{self.article.title}' em {self.timestamp.strftime('%d/%m/%Y %H:%M')}"
