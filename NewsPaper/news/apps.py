from django.apps import AppConfig


class RestConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'news'

    # нам надо переопределить метод ready, чтобы при готовности нашего приложения импортировался модуль со всеми функциями обработчиками
    def ready(self):
        import news.signals
        
        # from .tasks import sendMails
        # from .scheduler import news_scheduler
        # print('STARTED')
        
        # news_scheduler.add_job(
        #     id='send mails',
        #     func=sendMails,
        #     trigger = 'interval',
        #     seconds=10,
        # )

        # news_scheduler.start()