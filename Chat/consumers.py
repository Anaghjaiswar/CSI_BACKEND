import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

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
        try:
            text_data_json = json.loads(text_data)
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Invalid JSON format"}))
            return

        action = text_data_json.get("action", "send_message")

        if action == "send_message":
            if "message" not in text_data_json:
                await self.send(text_data=json.dumps({"error": "Missing 'message' field for send_message action."}))
                return

            # Existing code for sending a new message
            message = text_data_json["message"]
            sender = self.scope["user"]
            message_type = text_data_json.get('message_type', 'text')
            attachment = text_data_json.get("attachment", None)
            mentions = text_data_json.get("mentions", None)
            parent_message_id = text_data_json.get("parent_message_id", None)

            if sender.is_authenticated:
                sender_details = await sync_to_async(self.get_sender_details)(sender)
                parent_message = None

                if parent_message_id:
                    from .models import Message
                    try:
                        parent_message = await sync_to_async(Message.objects.get)(id=parent_message_id)
                    except Message.DoesNotExist:
                        await self.send(text_data=json.dumps({"error": "Parent message does not exist"}))
                        return
                    
                message_id, created_at = await self.save_message(message, message_type, sender, attachment, mentions,parent_message)
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "message": message,
                        "sender": sender_details,
                        "message_type": message_type,
                        "attachment": attachment,
                        "id": message_id,
                        "created_at": created_at.isoformat(),
                        "room": self.room_id,
                        "parent_message_id": parent_message_id,
                    },
                )
                if mentions:
                    from User.models import User
                    from Notification.models import Notification
                    room_name = await self.get_room_name(self.room_id)
                    for mentioned_user_id in mentions:
                        if mentioned_user_id == sender.id:
                            continue  
                        try:
                            user = await sync_to_async(User.objects.get)(id=mentioned_user_id)
                        except User.DoesNotExist:
                            continue

                        notification = await sync_to_async(Notification.objects.create)(
                            user=user,
                            event_type='chat_mention',
                            message=f"You were mentioned in {room_name} chat by {sender.first_name}",
                            is_read=False
                        )
                        notification_data = {
                            "id": notification.id,
                            "event_type": notification.event_type,
                            "message": notification.message,
                            "url": notification.url,
                            "created_at": notification.created_at.isoformat(),
                        }
                        # Send the notification to the mentioned user's notifications group
                        await self.channel_layer.group_send(
                            f"notifications_{user.id}",
                            {
                                "type": "send_notification",
                                "notification": notification_data,
                            }
                        )

            else:
                await self.send(text_data=json.dumps({"error": "User is not authenticated"}))

        elif action == "edit_message":
            # Handle editing an existing message
            message_id = text_data_json.get("message_id")
            new_content = text_data_json.get("new_content")

            if not message_id or not new_content:
                await self.send(text_data=json.dumps({
                    "error": "Both 'message_id' and 'new_content' are required for editing."
                }))
                return
            edited_message = await self.edit_existing_message(message_id, new_content)

            if edited_message:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message_edited",
                        "id": message_id,
                        "new_content": new_content,
                    },
                )
            else:
                await self.send(text_data=json.dumps({"error": "Editing failed."}))

        elif action == "react_message":
            message_id = text_data_json.get("message_id")
            reaction_type = text_data_json.get("reaction")
            if not message_id or not reaction_type:
                await self.send(text_data=json.dumps({
                    "error": "'message_id' and 'reaction' are required for react_message."
                }))
                return

            updated_message = await self.react_to_message(message_id, reaction_type)
            if updated_message:
                # Optionally, broadcast the updated reactions to everyone in the room
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message_reacted",
                        "id": message_id,
                        "reactions": updated_message.reactions,
                    },
                )
            else:
                await self.send(text_data=json.dumps({"error": "Reaction failed; message not found."}))


        elif action == "delete_message":
            # Handle deleting an existing message
            message_id = text_data_json.get("message_id")

            if message_id:
                deletion_success = await self.delete_existing_message(message_id)
                if deletion_success:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "chat_message_deleted",
                            "id": message_id,
                        },
                    )
                else:
                    await self.send(text_data=json.dumps({"error": "Deletion failed."}))
            else:
                await self.send(text_data=json.dumps({"error": "Message ID is required for deletion."}))

        elif action == "typing":
            sender = self.scope["user"]
            sender_details = await sync_to_async(self.get_sender_details)(sender)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_typing",
                    "sender": sender_details,
                    "is_typing": True,
                },
            )

        elif action == "stop_typing":
            sender = self.scope["user"]
            sender_details = await sync_to_async(self.get_sender_details)(sender)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_typing",
                    "sender": sender_details,
                    "is_typing": False,
                },
            )

        else:
            await self.send(text_data=json.dumps({"error": "Unknown action"}))


    @sync_to_async
    def edit_existing_message(self, message_id, new_content):
        from .models import Message  # Adjust the import as needed
        try:
            message = Message.objects.get(id=message_id)
            current_user = self.scope["user"]
            # Permission check: allow if the current user is the sender or has special permissions.
            if message.sender != current_user:
                return None 
            message.edit_message(new_content)
            return message
        except Message.DoesNotExist:
            return None

    @sync_to_async
    def delete_existing_message(self, message_id):
        from .models import Message  # Adjust the import as needed
        try:
            message = Message.objects.get(id=message_id)
            current_user = self.scope["user"]
            # Permission check: allow if the current user is the sender or has special permissions.
            if message.sender != current_user:
                return False
            message.delete_message()  # This performs a soft delete (sets is_deleted to True)
            return True
        except Message.DoesNotExist:
            return False
        
    @sync_to_async
    def react_to_message(self, message_id, reaction_type):
        from .models import Message
        try:
            message = Message.objects.get(id=message_id)
            # Load existing reactions or initialize an empty dictionary
            reactions = message.reactions or {}
            # Update the count for the given reaction type
            reactions[reaction_type] = reactions.get(reaction_type, 0) + 1
            message.reactions = reactions
            message.save()
            return message
        except Message.DoesNotExist:
            return None


    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        sender = event["sender"]
        message_type = event["message_type"]
        message_id = event['id']
        created_at = event['created_at']
        room = event['room']
        attachment = event.get("attachment", None)
        parent_message_id = event.get("parent_message_id", None)
        parent_message = None
        current_user = self.scope.get("user")
        is_self = False
        if current_user and current_user.is_authenticated:
            is_self = sender.get("id") == current_user.id

        if parent_message_id:
            from .models import Message
            try:
                parent_message_obj = await sync_to_async(
                    Message.objects.select_related("sender").get
                )(id=parent_message_id)
                parent_message = {
                    "id": parent_message_obj.id,
                    "content": parent_message_obj.content,
                    "sender": {
                        "id": parent_message_obj.sender.id,
                        "name": parent_message_obj.sender.first_name,
                        "photo": parent_message_obj.sender.photo.url if parent_message_obj.sender.photo else None,
                    },
                    "created_at": parent_message_obj.created_at.isoformat(),
                }
            except Message.DoesNotExist:
                parent_message = None


        # Send message to WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "message": message,
                    "sender": sender,
                    'message_type': message_type,
                    'id': message_id,
                    'is_self': is_self,
                    "attachment": attachment,
                    'created_at': created_at,
                    'room': room,
                    "parent_message": parent_message,
                }
            )
        )
    
    async def chat_message_edited(self, event):
        await self.send(text_data=json.dumps({
            "action": "edited",
            "id": event["id"],
            "new_content": event["new_content"],
        }))

    async def chat_message_deleted(self, event):
        await self.send(text_data=json.dumps({
            "action": "deleted",
            "id": event["id"],
        }))

    async def chat_message_reacted(self, event):
        await self.send(text_data=json.dumps({
            "action": "reacted",
            "id": event["id"],
            "reactions": event["reactions"],
        }))

    async def chat_typing(self, event):
        sender = event["sender"]
        current_user = self.scope.get("user")
        if current_user and current_user.is_authenticated and sender["id"] == current_user.id:
            return
        
        await self.send(text_data=json.dumps({
            "action": "typing",
            "sender": event["sender"],
            "is_typing": event["is_typing"],
        }))

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
    def save_message(self, content, message_type, sender, attachment=None, mentions=None,parent_message=None):
        from .models import Room, Message  
        from django.contrib.auth import get_user_model
        User = get_user_model() 
        """
        Save the message to the database and return its ID and created timestamp.
        """
        room = Room.objects.get(id=self.room_id)

        message = Message.objects.create(
            room=room,
            sender=sender,
            message_type=message_type,
            content=content,
            attachment=attachment,
            parent_message=parent_message,
        )
        if mentions:
            valid_mentions = room.members.filter(id__in=mentions)
            message.mentions.set(valid_mentions)
        return message.id, message.created_at
    
    @sync_to_async
    def get_room_name(self, room_id):
        from .models import Room
        room = Room.objects.get(id=room_id)
        return room.name
