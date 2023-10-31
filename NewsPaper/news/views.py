from django.shortcuts import render
from django.views import View # Импортируем простую вьюшку
from django.core.paginator import Paginator # Импортируем класс, позволяющий удобно осуществлять постраничный вывод

from typing import Any
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from .models import Post
from datetime import datetime

from .filters import PostFilter # импортируем недавно написанный фильтр
from .forms import PostForm # импортируем нашу форму

from django.urls import reverse_lazy

class PostsList(ListView):
    model = Post
    template_name = 'news/posts.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-id')
    paginate_by = 2 # поставим постраничный вывод в один элемент
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset()) # вписываем наш фильтр в контекст
        context['time_now'] = datetime.utcnow()
        context['value1'] = None
        context['form'] = PostForm()
        return context
    
    def post(self, request, *args, **kwargs):
        # self.object = self.get_object() # assign the object to the view
        # form = self.get_form()
        
        form = self.form_class(request.POST) # создаём новую форму, забиваем в неё данные из POST-запроса
        if form.is_valid(): # если пользователь ввёл всё правильно и нигде не накосячил, то сохраняем новый товар
            form.save()
        return super().get(request, *args, **kwargs)

class PostDetail(DetailView):
    model = Post
    template_name = 'news/post.html'
    context_object_name = 'post'

# class Posts(View):
#     def get(self, request):
#        posts = Post.objects.order_by('-id')
#        p = Paginator(posts, 1) # Создаём объект класса пагинатор, передаём ему список наших товаров и их количество для одной страницы
#        posts = p.get_page(request.GET.get('page', 1)) # Берём номер страницы из get-запроса. Если ничего не передали, будем показывать первую страницу
#        # Теперь вместо всех объектов в списке товаров хранится только нужная нам страница с товарами
#        data = {
#        'posts': posts,
#        'noFiltersPage' : True,
#        }

#        return render(request, 'news/posts.html', data)        
    
class Posts(ListView):
    model = Post
    template_name = 'news/posts.html'
    context_object_name = 'posts'
    queryset = Post.objects.order_by('-id')
    paginate_by = 5 # поставим постраничный вывод в один элемент
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['filter'] = PostFilter(self.request.GET, queryset=self.get_queryset()) # вписываем наш фильтр в контекст
        context['time_now'] = datetime.utcnow()
        context['value1'] = None
        context['noFiltersPage'] = True
        context['form'] = PostForm()
        return context    
        
    def post(self, request, *args, **kwargs):
        # self.object = self.get_object() # assign the object to the view
        # form = self.get_form()
        
        form = self.form_class(request.POST) # создаём новую форму, забиваем в неё данные из POST-запроса
        if form.is_valid(): # если пользователь ввёл всё правильно и нигде не накосячил, то сохраняем новый товар
            form.save()
        return super().get(request, *args, **kwargs)
    

# дженерик для получения деталей о поста
class PostDetailView(DetailView):
   template_name = 'news/post_detail.html'
   queryset = Post.objects.all()

# дженерик для создания объекта. Надо указать только имя шаблона и класс формы, который мы написали в прошлом юните. Остальное он сделает за вас
class PostCreateView(CreateView):
   template_name = 'news/post_create.html'
   form_class = PostForm
   

   def post(self, request, *args, **kwargs):
        # self.object = self.get_object() # assign the object to the view
        # form = self.get_form()
        
        form = self.form_class(request.POST) # создаём новую форму, забиваем в неё данные из POST-запроса
        if form.is_valid(): # если пользователь ввёл всё правильно и нигде не накосячил, то сохраняем новый товар
            form.save()
        return super().get(request, *args, **kwargs)
   

# дженерик для редактирования объекта
class PostUpdateView(UpdateView):
   template_name = 'news/post_create.html'
   form_class = PostForm
   success_url = reverse_lazy('news:posts')

   # метод get_object мы используем вместо queryset, чтобы получить информацию об объекте который мы собираемся редактировать
   def get_object(self, **kwargs):
       id = self.kwargs.get('pk')
       return Post.objects.get(pk=id)
   
#    def post(self, request, *args, **kwargs):
#         # self.object = self.get_object() # assign the object to the view
#         # form = self.get_form()
        
#         # form = self.form_class(request.POST) # создаём новую форму, забиваем в неё данные из POST-запроса
#         # if form.is_valid(): # если пользователь ввёл всё правильно и нигде не накосячил, то сохраняем новый товар
#         #     form.save()
#         return super().get(request, *args, **kwargs)   

# дженерик для удаления товара
class PostDeleteView(DeleteView):
   template_name = 'news/post_delete.html'
   queryset = Post.objects.all()
   success_url = reverse_lazy('news:posts') # не забываем импортировать функцию reverse_lazy из пакета django.urls