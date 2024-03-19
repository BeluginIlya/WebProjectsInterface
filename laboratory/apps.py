from django.apps import AppConfig


class LaboratoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'laboratory'


class PLCConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'plc'

    def ready(self):
        import threading
        from ..plc.connect_plc import start_threads  # замените "ваш_файл" на актуальный путь до вашего файла

        # Запускаем потоки при старте Django
        start_threads()