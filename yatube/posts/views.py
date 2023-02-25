from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from .models import Post, Group, User
from .forms import PostForm
from django.shortcuts import redirect

# from django.http import HttpResponse
# Create your views here.

POSTS_PER_PAGE = 10


'''def index(request):
    # Одна строка вместо тысячи слов на SQL:
    # в переменную posts будет сохранена
    # выборка из 10 объектов модели Post,
    # отсортированных по полю pub_date
    # по убыванию (от больших значений к меньшим)
    posts = Post.objects.all()[:POSTS_PER_PAGE]
    # В словаре context отправляем информацию в шаблон
    context = {
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)'''


def index(request):
    # post_list = Post.objects.all().order_by('-pub_date')
    # Если порядок сортировки определен в классе Meta модели,
    # запрос будет выглядеть так:
    post_list = Post.objects.all()
    # Показывать по 10 записей на странице.
    paginator = Paginator(post_list, POSTS_PER_PAGE)

    # Из URL извлекаем номер запрошенной страницы - это значение параметра page
    page_number = request.GET.get('page')

    # Получаем набор записей для страницы с запрошенным номером
    page_obj = paginator.get_page(page_number)
    # Отдаем в словаре контекста
    context = {
        'posts': page_obj,
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'group': group,
        'posts': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.filter(
        author__username=username).order_by('-pub_date')
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    post_count = post_list.count()
    context = {
        'username': username,
        'post_count': post_count,
        'page_obj': page_obj,
        'author': author,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    post_count = Post.objects.count()
    context = {
        'post': post,
        'post_count': post_count,
    }
    return render(request, 'posts/post_detail.html', context)


'''def post_create(request):
    if request.method == 'POST':
        form = CreatePost(request.POST or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('post:pofile', username = post.author)
        form = CreatePost(request.POST)
        return render(request, 'posts/create_post.html', {'form':form})
    form = CreatePost()
    return render(request, 'posts/create_post.html', {'form':form})'''


'''def post_create(request):



    return render(request, 'posts/create_post.html')'''


def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('profile:profile', username=post.author)
    template = 'posts/create_post.html'
    context = {

        'form': PostForm()
    }
    return render(request, template, context)


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user.id != post.author.id:
        return redirect('index:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect('index:post_detail', post_id=post_id)
    form = PostForm(instance=post)
    context = {
        'form': form,
        'is_edit': True,
        'text': form['text']
    }
    return render(request, 'posts/create_post.html', context)


'''def post_create(request):
    if request.method == 'POST':
        form = CreatePost(request.POST)
        if form.is_valid():
            form.save()
            return redirect('post:profile', username=request.username)
    template = 'posts/create_post.html'
    context = {

        'form': CreatePost()
    }
    return render(request, template, context)'''

# ПОСОМТРИ ПРО МЕТОД POST. Что это за хуетень вообще?
# И ПОСМОТРИ ПРО валидно/не валидно

# View-функция для страницы сообщества:


'''def group_posts(request, slug):
    # Функция get_object_or_404 получает по заданным критериям объект
    # из базы данных или возвращает сообщение об ошибке, если объект не найден.
    # В нашем случае в переменную group будут переданы объекты модели Group,
    # поле slug у которых соответствует значению slug в запросе
    group = get_object_or_404(Group, slug=slug)
    # Метод .filter позволяет ограничить поиск по критериям.
    # Это аналог добавления
    # условия WHERE group_id = {group_id}
    posts = group.posts.all()[:POSTS_PER_PAGE]
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)'''


'''def group_posts(request):
    template = 'posts/group_list.html'
    title = 'Здесь будет информация о группах проекта Yatube'
    context = {
        'title': title,
    }
    return render(request, template, context)'''
