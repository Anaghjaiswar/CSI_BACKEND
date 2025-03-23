# notifications/utils.py

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import DeviceToken
from firebase_admin import messaging

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

def send_push_notification_individual(user, title, body, click_action=None, extra_data=None):
    """
    Send a push notification to a user's registered Android devices using Firebase Cloud Messaging.
    
    :param user: User instance.
    :param title: Notification title.
    :param body: Notification body.
    :param click_action: Optional action string or deep-link for the notification.
    :param extra_data: Optional dictionary of additional data.
    :return: Response from the Firebase Admin SDK.
    """
    # Get all Android device tokens for the user
    tokens = list(user.device_tokens.filter(device_type=DeviceToken.ANDROID).values_list('device_token', flat=True))
    if not tokens:
        return None

    responses = []
    for token in tokens:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data={**(extra_data or {}), "click_action": click_action} if click_action else (extra_data or {}),
            token=token,
        )
        response = messaging.send(message)
        responses.append(response)
    return responses