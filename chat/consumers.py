import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from .models import ChatWindow, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        author_id = text_data_json.get('author', None)
        window_id = text_data_json.get('window', None)

        author = None
        window = None

        if author_id:
            try:
                author = await sync_to_async(User.objects.get)(id=author_id)
            except User.DoesNotExist:
                pass

        if window_id:
            try:
                window = await sync_to_async(ChatWindow.objects.get)(id=window_id)
            except ChatWindow.DoesNotExist:
                pass

        if message and author and window:
            # Create the message object and save it to the database
            new_message = await sync_to_async(Message.objects.create)(message=message, author=author, window=window)

            # Send the message to the window
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': new_message.message,
                    'author': new_message.author.username,
                    'window': new_message.window.id,
                }
            )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        author = event['author']
        window = event['window']

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'author': author,
            'window': window
        }))
