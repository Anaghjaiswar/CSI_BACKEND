"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from Chat.routing import websocket_urlpatterns as chat_websocket_urlpatterns
from core.middleware.drf_token_auth_middleware import TokenAuthMiddleware
from Notification.routing import websocket_urlpatterns as notification_websocket_urlpatterns

websocket_urlpatterns = chat_websocket_urlpatterns + notification_websocket_urlpatterns


# HTTP and WebSocket protocols
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddleware(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})  


