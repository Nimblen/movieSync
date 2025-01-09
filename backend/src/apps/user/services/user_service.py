from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from channels.db import database_sync_to_async

User = get_user_model()







def generate_token(user):
    """Generate a JWT token for the user."""
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)

def get_client_ip(request):
    """Retrieve the IP address of the client."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_client_device(request):
    """Retrieve the device of the client."""
    return request.META.get('HTTP_USER_AGENT')



@database_sync_to_async
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return AnonymousUser()