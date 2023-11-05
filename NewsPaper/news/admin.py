from django.contrib import admin
from .models import Author, Category, Post, PostCategory, Comment, SubscriberCategory

# напишем уже знакомую нам функцию обнуления товара на складе
def reset_Rates(modeladmin, request, queryset): # все аргументы уже должны быть вам знакомы, самые нужные из них это request — объект хранящий информацию о запросе и queryset — грубо говоря набор объектов, которых мы выделили галочками.
    queryset.update(rate=0)
    reset_Rates.short_description = 'Обнулить рейтинги' # описание для более понятного представления в админ панеле задаётся, как будто это объект

# создаём новый класс для представления товаров в админке
class PostAdmin(admin.ModelAdmin):
    # list_display — это список или кортеж со всеми полями, которые вы хотите видеть в таблице с товарами
    # list_display = [field.name for field in Post._meta.get_fields()] # генерируем список имён всех полей для более красивого отображения
    list_display = ['author', 'type_post', 'date_create', 'title', 'content', 'rate', 'FeaturedPost']
    list_filter = ('author', 'type_post') # добавляем примитивные фильтры в нашу админку
    search_fields = ('title', 'content', 'date_create') # тут всё очень похоже на фильтры из запросов в базу
    actions = [reset_Rates] # добавляем действия в список

# создаём новый класс для представления товаров в админке
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['author','rate']
    list_filter = ['author','rate'] # добавляем примитивные фильтры в нашу админку
    search_fields = ['author','rate'] # тут всё очень похоже на фильтры из запросов в базу
    actions = [reset_Rates] # добавляем действия в список    

# создаём новый класс для представления товаров в админке
class CommentAdmin(admin.ModelAdmin):
    list_display = ['post','user','comment','date_create','rate']
    list_filter = ['post','user','comment','date_create','rate'] # добавляем примитивные фильтры в нашу админку
    search_fields = ['post','user','comment','date_create','rate'] # тут всё очень похоже на фильтры из запросов в базу
    actions = [reset_Rates] # добавляем действия в список

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name']
    list_filter = ['category_name'] # добавляем примитивные фильтры в нашу админку
    search_fields = ['category_name'] # тут всё очень похоже на фильтры из запросов в базу

class PostCategoryAdmin(admin.ModelAdmin):
    list_display = ['post', 'category']
    list_filter = ['post', 'category'] # добавляем примитивные фильтры в нашу админку
    search_fields = ['post', 'category'] # тут всё очень похоже на фильтры из запросов в базу

class SubscriberCategoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'category']
    list_filter = ['user', 'category'] # добавляем примитивные фильтры в нашу админку
    search_fields = ['user', 'category'] # тут всё очень похоже на фильтры из запросов в базу      

admin.site.register(Author, AuthorAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory, PostCategoryAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(SubscriberCategory, SubscriberCategoryAdmin)


