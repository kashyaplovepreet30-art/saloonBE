from django.contrib import admin

from .models import Appointment, AppointmentAssignment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "appointment_number",
        "customer",
        "service",
        "staff",
        "appointment_date",
        "start_time",
        "end_time",
        "status",
        "payment_status",
    )
    list_filter = ("status", "payment_status", "appointment_date")
    search_fields = ("appointment_number", "customer__email", "customer__first_name")
    date_hierarchy = "appointment_date"


@admin.register(AppointmentAssignment)
class AppointmentAssignmentAdmin(admin.ModelAdmin):
    list_display = ("id", "appointment", "staff", "assigned_by", "assigned_at")
    search_fields = ("appointment__appointment_number", "staff__email")
