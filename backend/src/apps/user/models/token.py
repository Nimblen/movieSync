from django.db import models




class TokenBlackList(models.Model):
    token = models.CharField(max_length=255)