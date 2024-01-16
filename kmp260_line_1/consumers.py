import json
from channels.generic.websocket import AsyncWebsocketConsumer

from asgiref.sync import sync_to_async
import asyncio

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "WebInterfaceForProjects.settings")
django.setup()

from .views import LocalPrintHistoryAPI as base_view


class DataUpdatesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        print("Client connected")
        await self.channel_layer.group_add(
            'data_updates_group', 
            self.channel_name,
        )
        print("client added to group data_updates_group")


    async def disconnect(self, close_code):
        print("Client disconnected")


    async def data_updated(self, event):
        data = event['data']

        # Отправка обновленных данных клиенту через веб-сокет
        await self.send(text_data=json.dumps({
            'type': 'data.updated',
            'data': data,
        }))

    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        print("Сообщение от клиента: ",message)
        if message == "GET DATA":
            await async_update_table()

        response_data = {'status': 'success', 'message': 'Your response data here'}

        # Отправляем ответ клиенту
        await self.send(text_data=json.dumps(response_data))

async def async_update_table():
    # Получаем данные из базы данных асинхронно
    serialized_data = await sync_to_async(base_view.get_tabel_data_from_db)()

    # Обновляем таблицу асинхронно
    await sync_to_async(base_view.send_ws_data)(serialized_data, 'table_updated')
