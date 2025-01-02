from django.db import models
from src.apps.core.models.abstracts import TimeStampedModel



class Session(TimeStampedModel):
    user = models.ForeignKey("user.User", on_delete=models.CASCADE, related_name="sessions")
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True) 
    device = models.CharField(max_length=255, default="web")
    ip_address = models.GenericIPAddressField(default="127.0.0.1")
    last_activity = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.user.username} - {self.device}"



