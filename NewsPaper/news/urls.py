from django.contrib import admin
from django.urls import path, include
from .views import PostsList, PostDetail ,Posts, PostCreateView, PostDeleteView, PostUpdateView, PostDetailView 
from .views import upgrade_me, subscribe_me 

from django.views.decorators.cache import cache_page

app_name = 'news'
urlpatterns = [
    # path -- означает путь. В данном случае путь ко всем товарам у нас останется пустым, позже станет ясно почему
    path('', cache_page(60*1)(Posts.as_view()), name='posts'), # т.к. сам по себе это класс, то нам надо представить этот класс в виде view. Для этого вызываем метод as_view
    # path('<int:pk>', PostDetail.as_view()),
    
    path('<int:pk>/', PostDetailView.as_view(), name='post_detail'), # Ссылка на детали поста
    path('add/', PostCreateView.as_view(), name='post_create'), # Ссылка на создание поста
    path('<int:pk>/update/', PostUpdateView.as_view(), name='post_update'), # Ссылка на редактирование поста
    path('<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'), # Ссылка на удаеление поста
 
    path('search/', PostsList.as_view()), # Не забываем добавить эндпойнт для нового класса-представления. 
    path('upgrade/', upgrade_me, name = 'upgrade'),
    path('<int:pk>/subscribe/', subscribe_me, name='subscribe'), # Ссылка на подписку
]