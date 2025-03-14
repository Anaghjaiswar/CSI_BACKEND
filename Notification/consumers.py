# notifications/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Ensure that only authenticated users can connect
        self.user = self.scope["user"]
        if self.user.is_anonymous:
            await self.close()
        else:
            # Use a unique group for each user
            self.group_name = f"notifications_{self.user.id}"
            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        print(self)
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        # Currently, we're not processing client-sent messages.
        pass

    async def send_notification(self, event):
        """
        Called when a notification is sent to this group.
        The event dict should contain a 'notification' key.
        """
        notification = event["notification"]
        # Send the notification data to the client
        await self.send(text_data=json.dumps({
            "notification": notification
        }))
