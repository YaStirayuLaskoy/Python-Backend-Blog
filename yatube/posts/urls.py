from django.urls import path
from . import views

app_name = 'index'
app_name = 'posts'
app_name = 'profile'

urlpatterns = [
    path('', views.index, name='main'),
    path('group/<slug:slug>/', views.group_posts, name='group_list'),
    path('create/', views.post_create, name='post_create'),
    path('<str:username>/', views.profile, name='profile'),
    path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
    path('posts/<int:post_id>/edit/', views.post_edit, name='post_edit'),
]

# 'posts:groups_posts'


# path('posts/<int:post_id>/', views.post_detail, name='post_detail'),
