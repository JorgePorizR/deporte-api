# sistemaapi/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PartidoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'partidos'

        # Unirse al grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Salir del grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Recibir mensaje desde el servidor
    async def send_notification(self, event):
        message = event.get('message', 'No message')

        try:
            await self.send(text_data=json.dumps({'message': message}))
        except Exception as e:
            print(f"Error sending message: {e}")
