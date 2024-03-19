from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .serializers import LocalPrintHistorySerializer
from .models import LocalPrintHistory


def get_data_and_update_table(data):
    channel_layer = get_channel_layer("default")

    async_to_sync(channel_layer.group_send)('data_updates_group', {
        'type': 'data.updated',
        'data': data,
    })

def get_tabel_data_from_db():
    latest_records = LocalPrintHistory.objects.order_by('-Timestamp', '-NumProd')[:10:-1]
    serialized_data = LocalPrintHistorySerializer(latest_records, many=True).data
    return serialized_data