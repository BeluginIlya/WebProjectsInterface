from django.urls import path
from .views import *
from plc.connect_plc import *
app_name = 'laboratory'

urlpatterns = [
    path('<int:line_number>/', lab_view, name='line_lab'),
    path('get_lines/', get_lines, name='get_lines'),
    path('get_sensors_data', get_sensors_data, name='get_sensors_data'),
    path('check_thread_status', check_thread_status, name='check_thread_status'),
]

