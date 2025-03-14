# notifications/utils.py

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def notify_user(user, notification_data):
    """
    Push a notification to the user's WebSocket group.
    :param user: The User instance
    :param notification_data: A dict containing notification details
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"notifications_{user.id}",
        {
            "type": "send_notification",
            "notification": notification_data,
        }
    )
