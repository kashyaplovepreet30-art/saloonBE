from django.contrib import admin

from .models import ItemRequest, StaffProfile


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "department", "status", "joining_date")
    list_filter = ("status", "department")
    search_fields = ("user__email", "user__first_name", "user__last_name")


@admin.register(ItemRequest)
class ItemRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "item", "quantity", "staff", "urgency", "status", "created_at")
    list_filter = ("status", "urgency", "created_at")
    search_fields = ("item", "reason", "staff__email")
