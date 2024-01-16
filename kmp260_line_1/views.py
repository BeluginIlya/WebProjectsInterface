import json

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from .serializers import LocalPrintHistorySerializer
from .models import LocalPrintHistory
from collections import OrderedDict


from django.shortcuts import render
from .models import LocalPrintHistory



def kpm_line_1_page(request):
    latest_records = LocalPrintHistory.objects.order_by('-Timestamp', '-NumProd')[:10]
    context = {
        'latest_records': latest_records[::-1],
    }

    return render(request, "kpm260_line_1/kpm260-line-1.html", context)


class LocalPrintHistoryAPI(APIView):
    def post(self, request, format=None):
        for item in request.data.values():
            # Проверяем, есть ли изделие с таким Timestamp и Barcode в базе данных
            existing_record = LocalPrintHistory.objects.filter(
                Timestamp=item['Timestamp'],
                Barcode=item['Barcode']
            ).first()

            if existing_record:
                # Если запись уже существует, пропускаем ее
                continue

            serializer = LocalPrintHistorySerializer(data=item)
            if serializer.is_valid():
                serializer.save()
                
                data = self.get_tabel_data_from_db()
                self.send_ws_data(data, 'table_updated')

        return Response(data, status=status.HTTP_201_CREATED)

    @classmethod
    def send_ws_data(cls, data, internal_type: str):
        
        channel_layer = get_channel_layer("default")

        send_data = {'internal_type': internal_type, 'event_data': data}
        send_json_data = json.dumps(send_data, ensure_ascii=False)  # Преобразование в JSON-строку


        async_to_sync(channel_layer.group_send)('data_updates_group', {
            'type': 'data.updated',
            'data': send_json_data,
        })


    @classmethod
    def get_tabel_data_from_db(cls):
        latest_records = LocalPrintHistory.objects.order_by('-Timestamp', '-NumProd')[:10:-1]
        serialized_data = LocalPrintHistorySerializer(latest_records, many=True).data
        regular_data = [dict(item) for item in serialized_data]
        return regular_data
    

class PrintStatusAPI(APIView):
    def post(self, request, format=None):
        print("Данные о статусе печати: ", request.data)

        LocalPrintHistoryAPI.send_ws_data(request.data, 'status_updated')

        return Response('OK', status=status.HTTP_200_OK)