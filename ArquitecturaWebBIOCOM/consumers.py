# consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificacionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            # Rechazar la conexión si el usuario no está autenticado
            await self.close()
        else:
            self.user_group_name = f'user_{self.user.id}'
            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

    # Recibe notificaciones del servidor
    async def send_notification(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))