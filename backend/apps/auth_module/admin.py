from django.contrib import admin

from apps.auth_module.models import PasswordResetOTP, User, UserProfile, UserSession

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(PasswordResetOTP)
admin.site.register(UserSession)
