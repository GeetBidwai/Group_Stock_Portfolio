from django.contrib import admin

from apps.auth_module.models import User, UserProfile, UserSession

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(UserSession)
