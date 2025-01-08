from rest_framework import serializers


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

