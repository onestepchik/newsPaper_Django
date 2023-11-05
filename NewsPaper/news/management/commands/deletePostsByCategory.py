from django.core.management.base import BaseCommand, CommandError
from news.models import Post, Category

class Command(BaseCommand):
    help = 'Удаление всех постов определенной категории'
 
    def add_arguments(self, parser):
        parser.add_argument('category', type=str)
 
    def handle(self, *args, **options):
        answer = input(f'Вы правда хотите удалить все статьи в категории {options["category"]}? yes/no')
 
        if answer != 'yes':
            self.stdout.write(self.style.ERROR('Отменено'))
 
        try:
            for post in Post.objects.all():
                categories = post.categories.all()
                for cat in categories:
                    if cat.category_name == options['category']:
                        post.delete()
                        break

            self.stdout.write(self.style.SUCCESS(f'Succesfully deleted all news from category {options["category"]}')) # в случае неправильного подтверждения говорим, что в доступе отказано
        except Post.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Could not find category {options["category"]} '))