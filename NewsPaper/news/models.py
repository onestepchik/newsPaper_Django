from django.db import models
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models import Sum

class Author(models.Model):
    author = models.OneToOneField(User, on_delete = models.CASCADE)
    rate = models.IntegerField()
    
    def update_rating(self):
        print("Выборка всех статей автора.")
        total_rate = 0
        total_rate += Post.objects.filter(author = self).aggregate(Sum("rate"))["rate__sum"]*3
        
        print("Выборка всех комментариев автора")
        total_rate += Comment.objects.filter(user = User.objects.get(username=self.author.username)).aggregate(Sum("rate"))["rate__sum"]
        
        print("Выборка всех комментариев к статьям автора")
        total_rate += Comment.objects.filter(post__author = self).aggregate(Sum("rate"))["rate__sum"]
        self.rate = total_rate
        self.save()

    def __str__(self):
       return f'{self.author.username}'

class Category(models.Model):
    category_name = models.CharField(max_length = 255, unique=True)
    subscribers = models.ManyToManyField(User, through = 'SubscriberCategory')
    def __str__(self):
       return f'{self.category_name}'

class SubscriberCategory(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    category = models.ForeignKey(Category, on_delete = models.CASCADE)

class Post(models.Model):
    type_Article = 'AR'
    type_New = 'NE'
    
    TYPES = [
        (type_Article, 'Статья'),
        (type_New, 'Новость')
    ]
    
    author = models.ForeignKey(Author, on_delete = models.CASCADE)
    type_post = models.CharField(max_length = 255, choices=TYPES, default=type_Article)
    date_create = models.DateTimeField(auto_now_add = True)
    categories = models.ManyToManyField(Category, through = 'PostCategory')
    title = models.CharField(max_length = 255)
    content =  models.TextField(default = "Текст новости/статьи")
    rate = models.IntegerField(default = 0)

    @property
    def FeaturedPost(self):
        return self.rate > 10
    
    def __str__(self):
        return f'{self.title}'
    
    def like(self):
        self.rate+=1
        self.save()
    def dislike(self):
        self.rate-=1
        self.save()
    def preview(self):
        return self.content[:124] + "..."
    def get_absolute_url(self): # добавим абсолютный путь, чтобы после создания нас перебрасывало на страницу с постом
       return f'/post/{self.id}'
    
    
class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    category = models.ForeignKey(Category, on_delete = models.CASCADE)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    comment =  models.TextField(default = "Текст комментария")
    date_create = models.DateTimeField(auto_now_add = True)
    rate = models.IntegerField(default = 0)

    def like(self):
        self.rate+=1
        self.save()
    def dislike(self):
        self.rate-=1
        self.save()