from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from .forms import ArticleForm, LoginForm
from rest_framework import generics
from .serializers import ArticleSerializer
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils import timezone
from .models import Article, AuditLog
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm


# Função de login do usuário
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                create_audit_log(request.user, action="Login realizado")
                messages.success(request, 'Login realizado com sucesso!')
                return redirect(request.GET.get('next', 'home'))
            else:
                messages.error(request, 'Nome de usuário ou senha incorretos.')
    else:
        form = LoginForm()
    return render(request, 'app_project/templates/registration/login.html', {'form': form})


@login_required
def user_logout(request):
    create_audit_log(request.user, action="Logout realizado")
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
    articles = Article.objects.all()
    query = request.GET.get('q', '')  # Certifique-se de capturar a consulta de pesquisa

    # Filtragem dos artigos se houver uma consulta
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(authors__icontains=query) |
            Q(keywords__icontains=query)
        )
    if sort_by in ['title', 'date', 'authors']:
        articles = articles.order_by(sort_by if sort_by != 'date' else '-date')
    return render(request, 'app_project/article_list.html', {'articles': articles, 'sort_by': sort_by, 'query': query})


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
            article.created_by = request.user  # O usuário atual cria o artigo
            article.save()

            # Criar log de auditoria com a função create_audit_log
            create_audit_log(
                user=request.user,
                action=f"Criou o artigo: {article.title}",
                article=article,
                details=f"Artigo '{article.title}' criado com sucesso."
            )

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
            # Adapte conforme a estrutura de histórico de artigos (se necessário)
            form.save()

            # Criar log de auditoria com a função create_audit_log
            create_audit_log(
                user=request.user,
                action=f"Atualizou o artigo: {article.title}",
                article=article,
                details=f"Artigo '{article.title}' atualizado."
            )

            messages.success(request, 'Artigo atualizado com sucesso!')
            return redirect('article_detail', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'app_project/article_form.html', {'form': form})


# Função para deletar um artigo
@login_required
def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)

    # Verifica se o usuário tem permissão para excluir
    if not request.user.has_perm('app_project.delete_article'):
        return HttpResponseForbidden("Você não tem permissão para excluir este artigo.")

    # Caso o usuário tenha permissão e o método seja POST, exclui o artigo e registra no AuditLog
    if request.method == "POST":
        create_audit_log(
            user=request.user,
            action=f"Deletou o artigo: {article.title}",
            article=article,
            details=f"Artigo '{article.title}' deletado."
        )

        # Exclui o artigo
        article.delete()
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


@login_required
def profile(request):
    return render(request, 'profile.html', {'user': request.user})


def user_not_authenticated(user):
    return not user.is_authenticated


@user_passes_test(user_not_authenticated, login_url='/')
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Faz login automaticamente após o registro
            messages.success(request, 'Sua conta foi criada com sucesso! Faça login para continuar.')  # Mensagem de sucesso
            return redirect('/')  # Redireciona para a página inicial
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def create_audit_log(user, action, article=None, details=None):
    if not user:
        print("No user found when creating audit log.")
    AuditLog.objects.create(
        user=user,
        action=action,
        description=details if details else "Ação registrada no sistema.",
        timestamp=timezone.now()
    )
