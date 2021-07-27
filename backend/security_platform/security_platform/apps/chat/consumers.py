"""
websocket接口处理
"""
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger('websocket')


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data = str(text_data)
        # logger.info('addr:%s', self.room_name)
        # logger.info('data:%s', text_data)

        try:
            text_data_json = json.loads(text_data)
            publisher = text_data_json.get('publisher')
            del text_data_json['publisher']
        except Exception:
            logger.warning('json解析数据失败')
        else:
            if publisher:
                # Send message to room group
                message = text_data_json
                await self.channel_layer.group_send(self.room_group_name, {'type': 'chat_message', 'message': message})

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))
