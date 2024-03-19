from django.urls import path
from .views import *
from .connect_plc import *
app_name = 'laboratory'

urlpatterns = [
    path('<int:line_number>/', lab_view, name='line_lab'),
    path('get_lines/', get_lines, name='get_lines'),
    path('create_line/', create_line, name='create_line'),
    path('start_plc_data_collection', start_plc_data_collection, name='start_plc_data_collection'),
    path('stop_plc_data_collection', stop_plc_data_collection, name='stop_plc_data_collection'),
    path('get_temperature_data', get_temperature_data, name='get_temperature_data'),
    path('get_humidity_data', get_humidity_data, name="get_humidity_data")
]

