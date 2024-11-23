# Generated by Django 4.2.15 on 2024-09-09 16:40

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_project', '0002_alter_article_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='abstract',
            field=models.TextField(validators=[django.core.validators.MinLengthValidator(100), django.core.validators.MaxLengthValidator(1000)]),
        ),
        migrations.AlterField(
            model_name='article',
            name='authors',
            field=models.CharField(max_length=500, validators=[django.core.validators.RegexValidator(message='Use um formato válido: "Sobrenome, Nome; Sobrenome, Nome".', regex='^[A-Za-zÀ-ÖØ-öø-ÿ,;\\s]+$')]),
        ),
        migrations.AlterField(
            model_name='article',
            name='date',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2024)]),
        ),
        migrations.AlterField(
            model_name='article',
            name='keywords',
            field=models.CharField(max_length=255, validators=[django.core.validators.RegexValidator(message='As palavras-chave devem ser separadas por vírgulas.', regex='^[A-Za-zÀ-ÖØ-öø-ÿ,\\s]+$')]),
        ),
        migrations.AlterField(
            model_name='article',
            name='pdf_file',
            field=models.FileField(upload_to='http://127.0.0.1:8000/article/7/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf'])]),
        ),
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(max_length=200, validators=[django.core.validators.MinLengthValidator(10)]),
        ),
    ]