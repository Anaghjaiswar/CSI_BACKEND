from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async

class TokenAuthMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope['query_string'].decode()
        query_params = parse_qs(query_string)
        token_key = query_params.get('token')

        if token_key:
            token_key = token_key[0]
            user = await self.get_user(token_key)
            scope['user'] = user
        else:
            scope['user'] = AnonymousUser()

        return await self.inner(scope, receive, send)

    @database_sync_to_async
    def get_user(self, token_key):
        try:
            token = Token.objects.get(key=token_key)
            return token.user
        except Token.DoesNotExist:
            return AnonymousUser()
