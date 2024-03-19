from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from datetime import datetime, timedelta


from .models import CurtecSensors
from django.shortcuts import render, redirect
from .models import Line, PLC
from .forms import LineForm

def lab_view(request, line_number):
    line_name = f"Линия {line_number}"

    lines = Line.objects.all()

    plcs = PLC.objects.filter(line__id=line_number)

    unique_chambers = plcs.values('chamber').distinct()

    context = {
        'line_name': line_name,
        'lines': lines,
        'line_id': line_number,            
        'unique_chambers': unique_chambers, 
    }

    return render(request, 'laboratory/line_lab.html', context)



def get_temperature_data(request):
    line_id = request.GET.get('line_id')
    chamber = request.GET.get('chamber')
    start_date = request.GET.get('start_date')

    end_time = datetime.now()

    if start_date:
        start_time = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        # Если start_date не указан, вы можете установить другой логикой начальное время, если нужно
        start_time = end_time - timedelta(hours=24)  # Например, за последние 24 часа

    temperature_data = CurtecSensors.objects.filter(
        PLC__line__id=line_id,
        PLC__chamber=chamber,
        TimeStamp__gte=start_time,
        TimeStamp__lte=end_time,
        ValueName='Air TemperatureЛиния 4'  # Подставьте соответствующее имя, если у вас используются различные датчики
    ).values('TimeStamp', 'Value')

    labels = [entry['TimeStamp'].strftime('%Y-%m-%d %H:%M:%S') for entry in temperature_data]
    values = [entry['Value'] for entry in temperature_data]

    data = {'labels': labels, 'values': values}
    return JsonResponse(data)


def get_humidity_data(request):
    line_id = request.GET.get('line_id')
    chamber = request.GET.get('chamber')
    start_date = request.GET.get('start_date')

    end_time = datetime.now()

    if start_date:
        start_time = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        # Если start_date не указан, вы можете установить другой логикой начальное время, если нужно
        start_time = end_time - timedelta(hours=24)  # Например, за последние 24 часа

    temperature_data = CurtecSensors.objects.filter(
        PLC__line__id=line_id,
        PLC__chamber=chamber,
        TimeStamp__gte=start_time,
        TimeStamp__lte=end_time,
        ValueName='MotorЛиния 4'  # Подставьте соответствующее имя, если у вас используются различные датчики
    ).values('TimeStamp', 'Value')

    labels = [entry['TimeStamp'].strftime('%Y-%m-%d %H:%M:%S') for entry in temperature_data]
    values = [entry['Value'] for entry in temperature_data]

    data = {'labels': labels, 'values': values}
    return JsonResponse(data)




def get_lines(request):
    lines = Line.objects.all()

    lines_data = [{'id': line.id, 'name': line.LineName} for line in lines]

    return JsonResponse({'lines': lines_data})


def create_line(request):
    if request.method == 'POST':
        form = LineForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = LineForm()
    return render(request, 'laboratory/create_line.html', {'form': form})
