from rest_framework import serializers
from app_project.models import Article  # Ajuste para o nome do seu modelo de artigo

class ArtigoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
