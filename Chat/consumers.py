import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Room, Message 

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name,
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        sender = self.scope["user"]
        message_type = text_data_json.get('message_type', 'text')  # Default to 'text'
        attachment = text_data_json.get("attachment", None)  # Attachment URL or path



        # Check if the user is authenticated to avoid the AnonymousUser error
        if sender.is_authenticated:
            sender_name = sender.first_name or sender.username
            message_id, created_at = await self.save_message(message, message_type, sender, attachment)

            sender_details = await sync_to_async(self.get_sender_details)(sender)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",  # Event type
                    "message": message,
                    "sender": sender_details,
                    'message_type': message_type,
                    "attachment": attachment,
                    'id': message_id,
                    'created_at': created_at.isoformat(),
                    'room': self.room_name,
                },
            )
        else:
            # Handle unauthenticated users (optional)
            await self.send(
                text_data=json.dumps({"error": "User is not authenticated"})
            )
            # print(sender_name)
            print(sender)

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]
        message_type = event["message_type"]
        message_id = event['id']
        created_at = event['created_at']
        room = event['room']
        attachment = event.get("attachment", None)


        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "sender": sender,
                    'message_type': message_type,
                    'id': message_id,
                    "attachment": attachment,
                    'created_at': created_at,
                    'room': room,
                }
            )
        )

    def get_sender_details(self, sender):
        """
        Get the sender details to send with the message.
        """
        sender_name = sender.first_name
        sender_id = sender.id
        sender_role = getattr(sender, 'role', 'User')
        sender_photo = None
        if hasattr(sender, 'photo') and sender.photo:
            sender_photo = sender.photo.url 

        return {
            "name": sender_name,
            "photo": sender_photo,
            "id": sender_id,
            "role": sender_role,
        }
    
    @sync_to_async
    def save_message(self, content, message_type, sender, attachment=None):
        """
        Save the message to the database and return its ID and created timestamp.
        """
        message = Message.objects.create(
            room=Room.objects.get(name=self.room_name),
            sender=sender,
            message_type=message_type,
            content=content,
            attachment=attachment,
        )
        return message.id, message.created_at
