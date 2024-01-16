from datetime import datetime
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.views import APIView
from .models import LocalPrintHistory
from .serializers import LocalPrintHistorySerializer

from django.shortcuts import render
from .models import LocalPrintHistory

def kpm_line_1(request):
    # Get the latest 10 records from the LocalPrintHistory model
    latest_records = LocalPrintHistory.objects.order_by('-Timestamp', '-NumProd')[:10]

    # Pass the records to the template context
    context = {
        'latest_records': latest_records[::-1],
    }

    return render(request, "kpm260_line_1/kpm260-line-1.html", context)


class LocalPrintHistoryAPI(APIView):
    def post(self, request, format=None):
        print(request.data)
        for item in request.data.values():
            serializer = LocalPrintHistorySerializer(data=item)
            if serializer.is_valid():
                # existing_record_by_barcode = LocalPrintHistory.objects.filter(Barcode=item['Barcode']).first()
                # print(f"{'Запись уже существует'if existing_record_by_barcode else 'ок'}" )

                # if not (existing_record_by_barcode):
                #     # If the record does not exist, create a new one
                serializer.save()

        # Получаем актуальные данные из базы данных
        latest_records = LocalPrintHistory.objects.all()
        serialized_data = LocalPrintHistorySerializer(latest_records, many=True).data

        return Response(serialized_data, status=status.HTTP_201_CREATED, safe=False)
        