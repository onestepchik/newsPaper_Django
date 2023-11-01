from django.forms import ModelForm
from .models import Post
from django import forms

from allauth.account.forms import SignupForm
from django.contrib.auth.models import Group

# Создаём модельную форму
class PostForm(ModelForm):
# В класс мета, как обычно, надо написать модель, по которой будет строиться форма, и нужные нам поля. Мы уже делали что-то похожее с фильтрами
   class Meta:
       model = Post
       fields = ['author', 'type_post', 'categories','title','content','rate']
       widgets = {
         'title' : forms.TextInput(attrs={
           'class': 'form-control',
           'placeholder': 'Заголовок'
         }),
         'rate' : forms.TextInput(attrs={
           'type': 'number',
           'class': 'form-control',
           'value' : 0
         }),
         'author' : forms.Select(attrs={
           'class': 'form-control',
         }),

         'type_post' : forms.Select(attrs={
           'class': 'form-control',
         }),

         'content' : forms.Textarea(attrs={
           'class': 'form-control',
         }),
       }
    # author = models.ForeignKey(Author, on_delete = models.CASCADE)
    # type_post = models.CharField(max_length = 255, choices=TYPES, default=type_Article)
    # date_create = models.DateTimeField(auto_now_add = True)
    # categories = models.ManyToManyField(Category, through = 'PostCategory')
    # title = models.CharField(max_length = 255)
    # content =  models.TextField(default = "Текст новости/статьи")
    # rate = models.IntegerField(default = 0)



class BasicSignupForm(SignupForm):
  
   def save(self, request):
       user = super(BasicSignupForm, self).save(request)
       basic_group = Group.objects.get_or_create(name='common')[0]
       basic_group.user_set.add(user)
       return user
       