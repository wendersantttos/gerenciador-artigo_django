from rest_framework import serializers
from .models import Article
import datetime


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
