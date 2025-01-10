import jwt
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.conf import settings
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class JWTAuthMiddleware(BaseMiddleware):


    async def __call__(self, scope, receive, send):
        from rest_framework_simplejwt.tokens import AccessToken
        from django.contrib.auth.models import AnonymousUser
        from src.apps.user.services.user_service import get_user
        query_string = scope.get("query_string", b"").decode()
        params = dict(param.split('=') for param in query_string.split('&') if '=' in param)
        token = params.get("token", None)

        if token:
            try:
                AccessToken(token)
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get("user_id")
                if not user_id:
                    raise ValueError("User ID is missing in token payload")
                user = await get_user(user_id)
                scope["user"] = user
            except (InvalidToken, TokenError, jwt.DecodeError):
                scope["user"] = AnonymousUser()
        else:
            scope["user"] = AnonymousUser()

        return await super().__call__(scope, receive, send)
