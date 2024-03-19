import threading
import time
from datetime import datetime
import logging
from django.apps import apps
from laboratory.models import Line, PLC
from laboratory.msbd import DatabaseLineManager

from colorama import Fore, Style

from .connect_plc import PLC_Semiens

logging.basicConfig(filename='output_log.txt', level=logging.INFO, format='%(asctime)s %(message)s')

def process_line(line: Line):
    """Отдельный поток под каждую линию, для работы с каждым ПЛК:
        чтение данных с ПЛК и запись в бд"""
    
    logging.info(f"Процесс для линии {line.id}")
    error_dict = dict() # ключи для ошибок записываем как '{plc_interface.PLCName}_{plc_interface.chamber}'
    line_id = line.id
    db_manager = DatabaseLineManager(int(line_id))
    db_manager.connect()
    plc_list = PLC.objects.filter(line_id=line_id)
    plc_objects: dict[str:PLC_Semiens] = dict()
    for plc_interface in plc_list:
        plc_obj = PLC_Semiens(plc_interface)
        plc_objects[f'{plc_interface.PLCName}_{plc_interface.chamber}'] = plc_obj

    time_update = line.TimeSecUpdate

    thread_name = threading.current_thread().name
    while True:
        print_log(thread_name, start=True, text="Цикл потока запущен")
        all_thread_names = get_all_thread_names()
        print_log(thread_name, f"Имена всех потоков: {all_thread_names}")
        for plc_name, plc in plc_objects.items():
            result_connect = plc.connect()
            if result_connect:
                current_date = datetime.now()
                if current_date.day == 19 and current_date.hour == 12:
                    db_manager.delete_old_data(180)
                print_log(thread_name, plc_name=plc_name, text="Успешное подключение к ПЛК ")
                data = plc.get_data()
                plc.disconnect()
                if data:
                    for value_name, value in data.items():
                        result = db_manager.insert_data(value_name, value)
                        if result: 
                            print_log(thread_name, plc_name=plc_name, text=f"Данные успешно записаны для {value_name} - {value}")
                            error_dict[f'{plc_name}'] = ''
                        else:
                            print_log(thread_name, plc_name=plc_name, text=f"Ошбика записи данных в бд {value_name} - {value}")
                            error_dict[f'{plc_name}'] = 'Ошбика записи данных в бд'
                else:
                    print_log(thread_name, f"Ошибка при получении данных ПЛК {plc_name}")
                    error_dict[f'{plc_name}'] = 'Ошибка при получении данных ПЛК'
            else:
                print_log(thread_name, "Не удалось подключиться к ПЛК ", plc_name=plc_name)

        print_log(thread_name, "Конец цикла потока", end=True)
        setattr(threading.current_thread(), 'error_info', error_dict)
        time.sleep(time_update)
        
        

def start_threads():
    all_lines = Line.objects.all()

    for line in all_lines:
        plcs_count = PLC.objects.filter(line_id=line).count()
        if plcs_count > 0:
            thread_id = f"line_{line.id}_thread"

            if not thread_exists(thread_id):
                print("Создаём поток ", thread_id)
                thread = threading.Thread(target=process_line, args=(line,), name=thread_id)
                thread.start()


def get_all_thread_names():
    all_threads = threading.enumerate()
    thread_names = [thread.name for thread in all_threads]
    return thread_names

def thread_exists(thread_name):
    all_threads = threading.enumerate()
    print(f"all threads: {all_threads}")
    return any(thread.name == thread_name for thread in all_threads)


def print_log(thread_name, text, start=False, end=False, plc_name=''):
    colored_text = f"{Fore.BLUE}{f"|{plc_name}-"  +text}{Style.RESET_ALL}"
    if start:
        print('-'* 70)
        print("-" * 20 +f"[{thread_name}]" + colored_text)
    if end:
        print("-" * 20 + f"[{thread_name}]" + colored_text)
        print('-'* 70)
    else:
        print("-" * 20 + f"[{thread_name}]" + colored_text)
