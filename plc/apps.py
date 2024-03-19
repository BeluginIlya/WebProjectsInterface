import os
from django.apps import AppConfig
from decouple import config

class PLCConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plc'
    initialized = config('MY_init', default='0', cast=bool)

    def ready(self):
        import threading
        from .tasks import start_threads

        if not self.initialized:
            print("Инициализация приложения")
            start_threads()
            os.environ['MY_init'] = '1'  # Установка переменной окружения
