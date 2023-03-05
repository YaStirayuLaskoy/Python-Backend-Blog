from django.shortcuts import render, get_object_or_404
from .models import Post, Group, User
from .forms import PostForm
from django.shortcuts import redirect
from .utils import get_paginator


def index(request):
    post_list = Post.objects.all()
    context = {
        'page_obj': get_paginator(request, post_list),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    context = {
        'page_obj': get_paginator(request, post_list),
        'group': group,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.all().order_by('-pub_date')
    post_count = post_list.count()
    context = {
        'username': username,
        'post_count': post_count,
        'page_obj': get_paginator(request, post_list),
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


def create_post(request):
    form = PostForm(request.POST or None)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            form.save()
            return redirect('posts:profile', username=post.author)
    template = 'posts/create_post.html'
    context = {
        'form': form,
        'is_edit': False
    }
    return render(request, template, context)


def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    if request.user.id != post.author.id:
        return redirect('posts:post_detail', post_id=post_id)
    if request.method == 'POST':
        form = PostForm(request.POST or None, instance=post)
        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
    form = PostForm(instance=post)
    context = {
        'form': form,
        'is_edit': True
    }
    return render(request, 'posts/create_post.html', context)
