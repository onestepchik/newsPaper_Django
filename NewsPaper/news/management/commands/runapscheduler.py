import logging
 
from django.conf import settings
 
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from news.models import Post, User, Category, SubscriberCategory
from datetime import date, datetime, timedelta, time
from django.utils import timezone 
from django.template.loader import render_to_string # импортируем функцию, которая срендерит наш html в текст
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives # импортируем класс для создание объекта письма с html
 
 
logger = logging.getLogger(__name__)
 
 
# наша задача по выводу текста на экран
# def my_job():
#     #  Your job processing logic here... 
#     print('hello from job')
 
 
# функция которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)
 
# функция рассылки дайджестов
def sendNewPostsByWeek():
    print('START SENDING NEWS!')
    dateBegin = date.today() - timedelta(days=7)
    dateEnd = date.today() + timedelta(days=1)
    posts_for_week = Post.objects.filter(date_create__range=(dateBegin, dateEnd))
    print(f'Всего найдено постов {len(posts_for_week)}')
    # Сначала мы должны получить всех подписчиков со всех новостей, которые мы отобрали
    pushUsers = []
    postsByUsers = {}
    for post in posts_for_week:
        for cat in post.categories.all():
            s = SubscriberCategory.objects.all().filter(category = cat).values('user')
            if len(s) > 0:
                for user in s:
                    # print(user['user'])
                    # print(pushUsers)
                     
                    if user['user'] not in pushUsers:
                        # userObj = User.objects.get(pk=user['user'])
                        pushUsers.append(user['user'])
                    
                    if user['user'] in postsByUsers.keys():
                        posts_for_mail = postsByUsers[user['user']]
                        if post not in posts_for_mail:
                            posts_for_mail.append(post)
                    else:
                        postsByUsers[user['user']] = []
                        posts_for_mail = postsByUsers[user['user']]
                        posts_for_mail.append(post)

    # Затем бежим по каждому пользователю отдельно, отбираем статьи, на категории которых он подписан
    print(f'Кол-во постов {len(posts_for_mail)}')
    print(f'Кол-во подписчиков {len(pushUsers)}')
    print(f'Подписчики {pushUsers}')
    for user in pushUsers:
        # Формируем письмо с общим списком статей с гиперссылками и отправляем
        # Я создал template для рассылки постов подписчику 'news/posts_for_subscriber.html'
        posts_for_subscriber = postsByUsers[user]
        userObj = User.objects.get(pk=user)
        html_content = render_to_string( 
                        'news/posts_for_subscriber.html',
                        {
                            'posts': posts_for_subscriber,
                            'userName':userObj.username
                        }
                    )
                            # в конструкторе уже знакомые нам параметры, да? Называются правда немного по другому, но суть та же.
        msg = EmailMultiAlternatives(
            subject=f'{post.author}',
            body=post.content, #  это то же, что и message
            from_email='ostapdev@epoha.ru',
            to=[userObj.email], # это то же, что и recipients_list
        )
        msg.attach_alternative(html_content, "text/html") # добавляем html
        msg.send() # отсылаем
        msg = None


    

class Command(BaseCommand):
    help = "Runs apscheduler."
 
    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")
        
        # добавляем работу нашему задачнику
        # scheduler.add_job(
        #     my_job,
        #     trigger=CronTrigger(second="*/10"),  # Тоже самое что и интервал, но задача тригера таким образом более понятна django
        #     id="my_job",  # уникальный айди
        #     max_instances=1,
        #     replace_existing=True,
        # )
        # logger.info("Added job 'my_job'.")
 
        scheduler.add_job(
            sendNewPostsByWeek,
            # Для тестирования лучше триггер сменить на каждые 10 секунд
            trigger=CronTrigger(second="*/10"),
            # trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
            id="sendNewPostsByWeek",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'sendNewPostsByWeek'."
        )

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )
 
        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")