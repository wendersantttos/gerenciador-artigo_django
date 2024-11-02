from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .models import Article, ArticleHistory, AuditLog, CustomUser
from .forms import ArticleForm, LoginForm
from rest_framework import generics
from .serializers import ArticleSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone

# Função de login do usuário
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None and isinstance(user, CustomUser):
                login(request, user)
                AuditLog.objects.create(user=user, action="Login bem-sucedido", timestamp=timezone.now())
                messages.success(request, 'Login realizado com sucesso!')
                return redirect(request.GET.get('next', 'home'))
            else:
                messages.error(request, 'Nome de usuário ou senha incorretos.')
    else:
        form = LoginForm()
    return render(request, 'app_project/login.html', {'form': form})

@login_required
def user_logout(request):
    AuditLog.objects.create(user=request.user, action="Logout realizado", timestamp=timezone.now())
    logout(request)
    messages.success(request, 'Logout realizado com sucesso!')
    return redirect('login')

@login_required
def minha_view_protegida(request):
    AuditLog.objects.create(user=request.user, action="Acessou a view protegida", timestamp=timezone.now())
    return render(request, 'app_project/protected_view.html')

# Lista e criação de artigos
class ArticleListCreateView(generics.ListCreateAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        AuditLog.objects.create(user=self.request.user, action="Criou um artigo", timestamp=timezone.now())
        serializer.save(created_by=self.request.user)  # Adiciona o criador do artigo

# Detalhes, atualização e exclusão de um artigo específico
class ArticleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

# Função para listar artigos com opção de ordenação e pesquisa
def article_list(request):
    sort_by = request.GET.get('sort', 'title')
    query = request.GET.get('q', '')  # Captura a busca aqui
    articles = Article.objects.all()

    if sort_by in ['title', 'date', 'authors']:
        articles = articles.order_by(sort_by if sort_by != 'date' else '-date')

    # Adiciona a lógica de busca para a página inicial
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(authors__icontains=query) |
            Q(keywords__icontains=query)
        )

    return render(request, 'app_project/article_list.html', {
        'articles': articles,
        'sort_by': sort_by,
        'query': query  # Passa a variável query (q) aqui
    })

# Função para exibir detalhes de um artigo
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    return render(request, 'app_project/article_detail.html', {'article': article})

# Função para criar um novo artigo
@login_required
def article_create(request):
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.created_by = request.user  # Define o criador do artigo
            article.save()
            AuditLog.objects.create(user=request.user, action=f"Criou o artigo: {article.title}", timestamp=timezone.now())
            messages.success(request, 'Artigo criado com sucesso!')
            return redirect('article_detail', pk=article.pk)
    else:
        form = ArticleForm()
    return render(request, 'app_project/article_form.html', {'form': form})

# Função para atualizar um artigo existente
@login_required
def article_update(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            # Salva as alterações no histórico antes de modificar
            ArticleHistory.objects.create(
                article=article,
                title=article.title,
                authors=article.authors,
                abstract=article.abstract,
                keywords=article.keywords
            )
            form.save()
            AuditLog.objects.create(user=request.user, action=f"Atualizou o artigo: {article.title}", timestamp=timezone.now())
            messages.success(request, 'Artigo atualizado com sucesso!')
            return redirect('article_detail', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'app_project/article_form.html', {'form': form})

# Função para deletar um artigo
@login_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if request.method == "POST":
        article.delete()
        AuditLog.objects.create(user=request.user, action=f"Deletou o artigo: {article.title}", timestamp=timezone.now())
        messages.success(request, 'Artigo deletado com sucesso!')
        return redirect('article_list')
    return render(request, 'app_project/article_delete.html', {'article': article})

# Função para buscar artigos
def search_view(request):
    query = request.GET.get('q', '')  # Use uma string vazia como padrão
    results = Article.objects.filter(
        Q(title__icontains=query) |
        Q(authors__icontains=query) |
        Q(keywords__icontains=query)
    ) if query else Article.objects.none()
    return render(request, 'app_project/search_results.html', {
        'results': results,
        'query': query  # Passa a variável query (q) para o template
    })
