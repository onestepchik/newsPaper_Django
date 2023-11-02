from django.shortcuts import render
from django.views import View # Импортируем простую вьюшку
from django.core.paginator import Paginator # Импортируем класс, позволяющий удобно осуществлять постраничный вывод

from typing import Any
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from .models import Post, Category, SubscriberCategory, User
from datetime import datetime

from .filters import PostFilter # импортируем недавно написанный фильтр
from .forms import PostForm # импортируем нашу форму

from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin

from django.shortcuts import redirect 
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin

from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives # импортируем класс для создание объекта письма с html
from datetime import datetime
 
 
from django.template.loader import render_to_string # импортируем функцию, которая срендерит наш html в текст


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
    
class Posts(LoginRequiredMixin, ListView):
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
        context['is_not_premium'] = not self.request.user.groups.filter(name = 'authors').exists()
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
class PostCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
   template_name = 'news/post_create.html'
   form_class = PostForm
   permission_required = ('news.add_post',
                          'news.change_post')

   def form_valid(self, form):
        result = super().form_valid(form)
        print("This is my newly created instance", self.object.pk)
        
        return result

   def post(self, request, *args, **kwargs):
        # self.object = self.get_object() # assign the object to the view
        # form = self.get_form()
        
        form = self.form_class(request.POST) # создаём новую форму, забиваем в неё данные из POST-запроса
        if form.is_valid(): # если пользователь ввёл всё правильно и нигде не накосячил, то сохраняем новый товар
            post = form.save()

            user = self.request.user
            needPush = False
            pushUsers = []
            for cat in post.categories.all():
                s = SubscriberCategory.objects.all().filter(category = cat).values('user')
                if len(s) > 0:
                    for user in s:
                        if user not in pushUsers:
                            pushUsers.append(user)
                            needPush = True

            for userForEmail in pushUsers:
                usr = User.objects.get(pk=userForEmail['user'])
                # получем наш html
                html_content = render_to_string( 
                    'news/post_created_email.html',
                    {
                        'post': post,
                        'userName':usr.username
                    }
                )
                
                # в конструкторе уже знакомые нам параметры, да? Называются правда немного по другому, но суть та же.
                msg = EmailMultiAlternatives(
                    subject=f'{post.author}',
                    body=post.content, #  это то же, что и message
                    from_email='ostapdev@epoha.ru',
                    to=[usr.email], # это то же, что и recipients_list
                )
                msg.attach_alternative(html_content, "text/html") # добавляем html
                msg.send() # отсылаем

        return super().get(request, *args, **kwargs)
   

# дженерик для редактирования объекта
class PostUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
   template_name = 'news/post_create.html'
   form_class = PostForm
   success_url = reverse_lazy('news:posts')
   permission_required = ('news.change_post')
   
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
class PostDeleteView(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):
   template_name = 'news/post_delete.html'
   queryset = Post.objects.all()
   success_url = reverse_lazy('news:posts') # не забываем импортировать функцию reverse_lazy из пакета django.urls
   permission_required = ('news.delete_post')

@login_required
def upgrade_me(request):
   user = request.user
   premium_group = Group.objects.get(name='authors')
   if not request.user.groups.filter(name='authors').exists():
       premium_group.user_set.add(user)
   return redirect('/news')

@login_required
def subscribe_me(request, **kwargs):
   user = request.user
   id = kwargs.get('pk')
   post = Post.objects.get(pk=id)
   needPush = False
   for cat in post.categories.all():
        s = SubscriberCategory.objects.all().filter(user = user, category = cat)
        if len(s) == 0:
            sc = SubscriberCategory(user = user, category = cat)
            sc.save()
            needPush = True
   if needPush == True:
       # Тут нужно добавить текущего юзера в подписку к категориям поста если его еще там нет в подписках
    html_content = render_to_string( 
                'news/post_created_email.html',
                {
                    'post': post,
                }
            )
 
            # в конструкторе уже знакомые нам параметры, да? Называются правда немного по другому, но суть та же.
    msg = EmailMultiAlternatives(
                subject=f'{post.author}',
                body=post.content, #  это то же, что и message
                from_email='ostapdev@epoha.ru',
                to=['ostap@epoha.ru'], # это то же, что и recipients_list
            )
    msg.attach_alternative(html_content, "text/html") # добавляем html
    msg.send() # отсылаем
       

   def get_object(self, **kwargs):
       id = self.kwargs.get('pk')
       return Post.objects.get(pk=id)
#    premium_group = Group.objects.get(name='authors')
#    if not request.user.groups.filter(name='authors').exists():
#        premium_group.user_set.add(user)
   return redirect('/news')