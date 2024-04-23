from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


class MyUserAdmin(UserAdmin):
    ordering = ['phone']


admin.site.register(User, MyUserAdmin)
