import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.db.models import Subquery, OuterRef, Max
from django.db.models import F


from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework import status

from .serializers import LocalPrintHistorySerializer
from .models import LocalPrintHistory
from .models import LocalPrintHistory



def kpm_line_1_page(request):
    latest_records = LocalPrintHistory.objects.order_by('-Timestamp', '-NumProd')[:4]
    ip_address = request.META.get('REMOTE_ADDR', None)
    port = request.META.get('SERVER_PORT', None)
    context = {
        'latest_records': latest_records[::-1],
        'ip_address': ip_address, 
        'port': port
    }

    return render(request, "kpm260_line_1/kpm260-line-1.html", context)



@api_view(['POST'])
def end_product(request):
    if request.method == "POST":
        data = request.data
        print("Информация об успешном завершении печати", data)
        
        # Используйте filter для поиска записи в базе данных
        existing_record = LocalPrintHistory.objects.filter(
            PalNo=data['PalNo'],
            Barcode=data['Barcode'],
            Timestamp=data['Timestamp']
        ).first()

        if existing_record:
            # Обновите поле StatusPrint на True
            existing_record.StatusPrint = True
            existing_record.save()

            # Сериализуйте и возвращайте обновленную запись, если это необходимо
            serializer = LocalPrintHistorySerializer(existing_record)

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response("Запись не найдена", status=status.HTTP_404_NOT_FOUND)

    else:
        return Response("OK", status=status.HTTP_418_IM_A_TEAPOT)



class LocalPrintHistoryAPI(APIView):
    def post(self, request, format=None):

        for item in request.data.values():
            # Проверяем, есть ли изделие с таким Timestamp и Barcode в базе данных
            existing_record = LocalPrintHistory.objects.filter(
                # Timestamp=item['Timestamp'], пока тестим, проверям по баркоду и номеру палеты
                Barcode=item['Barcode'],
                PalNo = item['PalNo']
            ).first()

            if existing_record:
                continue

            serializer = LocalPrintHistorySerializer(data=item)
            if serializer.is_valid():
                serializer.save()
                
                data = self.get_tabel_data_from_db()
                self.send_ws_data(data, 'table_updated')

        return Response(request.data, status=status.HTTP_201_CREATED)

    @classmethod
    def send_ws_data(cls, data, internal_type: str):
        
        channel_layer = get_channel_layer("default")

        send_data = {'internal_type': internal_type, 'event_data': data}
        send_json_data = json.dumps(send_data, ensure_ascii=False)  # Преобразование в JSON-строку


        async_to_sync(channel_layer.group_send)('data_updates_group', {
            'type': 'data.updated',
            'data': send_json_data,
        })


    # @classmethod
    # def get_tabel_data_from_db(cls):
    #     latest_records = LocalPrintHistory.objects.order_by('-Timestamp', '-PalNo','-NumProd')[:4:-1]
    #     serialized_data = LocalPrintHistorySerializer(latest_records, many=True).data
    #     regular_data = [dict(item) for item in serialized_data]
    #     return regular_data
        
    @classmethod
    def get_tabel_data_from_db(cls):
        first_two_entries = LocalPrintHistory.objects.order_by('-Timestamp')[:2]


        LocalPrintHistory.objects.exclude(pk__in=first_two_entries.values_list('pk', flat=True)).delete()

        subquery = (
            LocalPrintHistory.objects
            .values('PalNo')
            .annotate(max_timestamp=Max('Timestamp'))
            .order_by('-max_timestamp')[:1]
        )
        print("----------subquery--------------------",subquery)

        latest_records = (
            LocalPrintHistory.objects.filter(PalNo__in=Subquery(subquery.values('PalNo')))
            .order_by('-Timestamp', '-PalNo', '-NumProd')
            .values('PalNo', 'NumProd', 'Timestamp', 'Barcode', 'Product', 'StatusPrint')
        )[:2:-1]

        print("----------latest_records--------------------",latest_records)

        serialized_data = LocalPrintHistorySerializer(latest_records, many=True).data

        return serialized_data

    

class PrintStatusAPI(APIView):
    def post(self, request, format=None):
        print("Данные о статусе печати: ", request.data)

        LocalPrintHistoryAPI.send_ws_data(request.data, 'status_updated')

        return Response('OK', status=status.HTTP_200_OK)