from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
import json

class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            await self.accept()
            await self.set_online(user)
            await self.send(text_data=json.dumps({"status": "online"}))
        else:
            await self.close()

    async def disconnect(self, close_code):
        user = self.scope["user"]
        if user.is_authenticated:
            await self.set_offline(user)

    @sync_to_async
    def set_online(self, user):
        user.is_online = True
        user.save()

    @sync_to_async
    def set_offline(self, user):
        user.is_online = False
        user.save()
