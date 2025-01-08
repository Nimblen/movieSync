from django.contrib import admin

from src.apps.user.models import User, Session, TokenBlackList


admin.site.register(User)
admin.site.register(Session)
admin.site.register(TokenBlackList)