import threading
import time
import snap7
import struct

from .models import CurtecSensors, PLC, Line
from django.http import JsonResponse

plc_threads = {}


def read_and_save_data(plc_id, chamber, line_name, stop_event):
    print(plc_id)
    plc = PLC.objects.get(id=plc_id)

    client = snap7.client.Client()

    while not stop_event.is_set():
        try:
            if not client.get_connected():
                client.connect(plc.adress, 0, 1, 102)

            if client.get_connected():
                data_bytes = client.db_read(7, 0, 9)

                air_temp, motor, damper_status = struct.unpack('>ffB', data_bytes)
                motor = round(motor, 2)
                print("Запись данных: ", air_temp, motor)

                CurtecSensors.objects.create(ValueName=f'Air Temperature{line_name}', Value=air_temp, PLC=plc)
                CurtecSensors.objects.create(ValueName=f'Motor{line_name}', Value=motor, PLC=plc)

            time.sleep(60)

        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

    print("Поток завершен.")



def start_plc_thread(plc_id, chamber, line_name):
    thread_info = plc_threads.get((plc_id, chamber))

    if thread_info:
        print(f"Поток с ключами ({plc_id}, {chamber}) уже существует.")
        return

    thread_name = f"PLC_Thread_{plc_id}_{chamber}"
    print("Старт потока ", thread_name)

    stop_event = threading.Event()  # Создаем объект Event для управления завершением потока

    plc_thread = threading.Thread(name=thread_name, target=read_and_save_data, args=(plc_id, chamber, line_name, stop_event))
    plc_thread.daemon = True
    plc_thread.start()

    plc_threads[(plc_id, chamber)] = {'thread': plc_thread, 'stop_event': stop_event}
    print("Всего потоков", threading.active_count())


def stop_plc_thread(plc_id, chamber):
    print("Остановка потока")
    thread_info = plc_threads.get((plc_id, chamber))

    if thread_info:
        stop_event = thread_info['stop_event']
        stop_event.set()  # Устанавливаем флаг, чтобы поток завершил выполнение
        thread_info['thread'].join()  # Ждем завершения потока

        del plc_threads[(plc_id, chamber)]
        print("Успешно")
        print("Всего потоков", threading.active_count())
        return True
    else:
        print("Не Успешно")
        print("Всего потоков", threading.active_count())
        return False



def start_plc_data_collection(request):
    if request.method == 'POST':
        chamber = request.POST.get('chamber')
        line_id = request.POST.get('line_id')
        print("lineid", line_id)
        line = Line.objects.get(id=line_id)
        line_name =line.LineName
        

        try:
            plc = PLC.objects.get(line=line, chamber=chamber)
            plc_id = plc.id
            start_plc_thread(plc_id, chamber, line_name)

            return JsonResponse({'status': 'success', 'message': 'поток запущен.'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Ошибка при старте потока: {e}'})

    return JsonResponse({'status': 'error', 'message': 'Что-то пошло не так.'})


def stop_plc_data_collection(request):
    if request.method == 'POST':
        line_id = request.POST.get('line_id')
        chamber = request.POST.get('chamber')
        line = Line.objects.get(id=line_id)
        plc = PLC.objects.get(line=line, chamber=chamber)
        plc_id = plc.id
        success = stop_plc_thread(plc_id, chamber)

        if success:
            return JsonResponse({'status': 'success', 'message': 'Data collection stopped successfully.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Thread not found.'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
