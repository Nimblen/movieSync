from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from src.apps.user.models import User, Session
from src.apps.user.serializers.user_serializer import (
    UserSerializer,
    UserLoginSerializer,
    UserChangeSerializer,
)
from src.apps.user.services.user_service import get_client_ip, get_client_device


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserChangeSerializer
    custom_actions = ["login", "get_me"]

    def get_serializer_class(self):
        if self.action == "login":
            return UserLoginSerializer
        if self.action == "get_me":
            return UserSerializer
        return super().get_serializer_class()

    @action(methods=["POST"], detail=False, permission_classes=[AllowAny])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get("username")
        password = serializer.validated_data.get("password")
        ip_address = get_client_ip(request)
        device = get_client_device(request)
        user = authenticate(username=username, password=password)
        if user is None:
            return Response(
                {
                    "error": {
                        "code": "INVALID_CREDENTIALS",
                        "message": "Invalid username or password",
                    }
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )
        refresh = RefreshToken.for_user(user)
        session, _ = Session.objects.get_or_create(
            user=user, ip_address=ip_address, device=device
        )
        session.token = str(refresh)
        session.save()
        token_data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
        return Response(token_data, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False, permission_classes=[IsAuthenticated])
    def get_me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
