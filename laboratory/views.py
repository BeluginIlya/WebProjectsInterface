from django.shortcuts import render
from django.http import JsonResponse
from datetime import datetime, timedelta
import threading

from .models import Line, PLC
from .msbd import DatabaseLineManager, interpolation_data

def lab_view(request, line_number):
    line_name = f"Линия {line_number}"

    lines = Line.objects.all()

    plcs = PLC.objects.filter(line_id=line_number)

    unique_chambers = plcs.values('chamber').distinct()
    context = {
        'line_name': line_name,
        'lines': lines,
        'line_id': line_number,            
        'unique_chambers': unique_chambers, 
    }
    return render(request, 'laboratory/line_lab.html', context)


def get_sensors_data(request):
    """Получаем данные из серверной бд. Данные проходят интерполяцию для усреднения по сегментам,
        чтобы получить необходимое количество точек для графика"""
    
    sensor_type = request.GET.get('sensor_type')  # air_temp или humidity
    line_id = request.GET.get('line_id')
    chamber = request.GET.get('chamber')
    start_date = request.GET.get('start_date')
    end_data = request.GET.get('end_data')
    interpolation_points = int(request.GET.get('interpolation_points'))

    if not end_data or end_data == "undefined":
        end_data = datetime.now()
    else:
        end_data = datetime.strptime(end_data, '%Y-%m-%d')
        end_data = end_data.replace(hour=23, minute=59, second=59)

    if not start_date or start_date == "undefined":

        start_date = end_data - timedelta(hours=24)
    else:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')

    plc = PLC.objects.get(line_id=line_id, chamber=chamber)
    value_name = f'{plc.PLCName}_{plc.chamber}_{sensor_type}'

    db_manager = DatabaseLineManager(line_id)
    sensor_data = db_manager.get_data(value_name, start_time=start_date,
                                           end_time=end_data)  
    if sensor_data:
        
        interpolation_temperature_data = interpolation_data(sensor_data, interpolation_points)
        new_values, new_timestamps, _ = zip(*interpolation_temperature_data)

        formatted_timestamps = [timestamp.strftime('%d.%m %H:%M') for timestamp in new_timestamps]
        data = {'labels': formatted_timestamps, 'values': new_values, 'error': ''}
    else:
        data = {'labels': None, 'values': None, 'error': "Данные отсутствуют"}
    return JsonResponse(data)


def get_lines(request):
    lines = Line.objects.all()

    lines_data = [{'id': line.id, 'name': line.LineName} for line in lines]

    return JsonResponse({'lines': lines_data})


def check_thread_status(request):
    if request.method == 'GET':
        line_id = int(request.GET.get('line_id'))
        chamber = request.GET.get('chamber')
        plc = PLC.objects.get(line_id=line_id, chamber=chamber)
        plc_id = plc.id
        thread_info = get_thread_ids(line_id)

        if thread_info:
            status = 'running'
            exception_info = getattr(thread_info, 'error_info', None)
            if exception_info:
                return JsonResponse({'status': status, 'exception_info': exception_info})
            else:
                return JsonResponse({'status': status})
        else:
            return JsonResponse({'status': 'stopped'})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})


def get_thread_ids(line_id):
    thread_name = f"line_{line_id}_thread"
    for thread in threading.enumerate():
        if thread.name == thread_name:
            return thread

    return None