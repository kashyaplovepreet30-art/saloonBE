from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("id", "email", "username", "role", "phone", "is_active", "date_joined")
    list_filter = ("role", "is_active", "is_staff")
    search_fields = ("email", "username", "first_name", "last_name", "phone")
    ordering = ("-date_joined",)

    fieldsets = UserAdmin.fieldsets + (
        ("Role Information", {"fields": ("role", "phone", "profile_image", "is_verified")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Role Information", {"fields": ("role", "phone", "profile_image")}),
    )
