from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from app_project.models import Article 
from .serializers import ArtigoSerializer

class ArtigoViewSet(viewsets.ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArtigoSerializer
