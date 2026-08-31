from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("id", "transaction_id", "user", "order", "appointment", "amount", "method", "status")
    list_filter = ("status", "method", "created_at")
    search_fields = ("transaction_id", "user__email")
