from rest_framework import serializers

from accounts.serializers import UserSerializer
from services.models import Service

from .models import Appointment
from .utils import generate_time_slots, get_available_staff


class AppointmentSerializer(serializers.ModelSerializer):
    customer = UserSerializer(read_only=True)
    staff = UserSerializer(read_only=True)
    service_name = serializers.CharField(source="service.name", read_only=True)

    class Meta:
        model = Appointment
        fields = (
            "id",
            "appointment_number",
            "customer",
            "service",
            "service_name",
            "staff",
            "appointment_date",
            "start_time",
            "end_time",
            "duration_minutes",
            "customer_notes",
            "admin_notes",
            "completion_remarks",
            "payment_status",
            "status",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "appointment_number",
            "customer",
            "staff",
            "end_time",
            "duration_minutes",
            "status",
            "payment_status",
            "created_at",
            "updated_at",
        )


class BookAppointmentSerializer(serializers.ModelSerializer):
    service = serializers.PrimaryKeyRelatedField(queryset=Service.objects.all())

    class Meta:
        model = Appointment
        fields = ("service", "appointment_date", "start_time", "customer_notes")

    def validate(self, attrs):
        service = attrs["service"]
        date = attrs["appointment_date"]
        start_time = attrs["start_time"]

        from datetime import datetime, timedelta

        from django.conf import settings

        if service.status != "active":
            raise serializers.ValidationError({"service": "This service is not active."})

        opening = datetime.strptime(settings.SALON_OPENING_TIME, "%H:%M").time()
        closing = datetime.strptime(settings.SALON_CLOSING_TIME, "%H:%M").time()
        end_dt = datetime.combine(date, start_time) + timedelta(minutes=service.duration_minutes)

        if start_time < opening or start_time >= closing:
            raise serializers.ValidationError(
                {"start_time": "Appointments must be within salon hours (09:00 - 19:00)."}
            )
        if end_dt.time() > closing:
            raise serializers.ValidationError(
                {"start_time": "Service would exceed salon closing time."}
            )

        slots = generate_time_slots(service, date)
        matching = next(
            (s for s in slots if s["start"] == start_time), None
        )
        if not matching or not matching["available"]:
            raise serializers.ValidationError(
                {"start_time": "Selected appointment slot is no longer available."}
            )

        if not get_available_staff(service, date, start_time, end_dt.time()):
            raise serializers.ValidationError(
                {"start_time": "No staff member is available for the selected time."}
            )

        attrs["end_time"] = end_dt.time()
        attrs["duration_minutes"] = service.duration_minutes
        return attrs


class AssignStaffSerializer(serializers.Serializer):
    staff_id = serializers.IntegerField()
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_staff_id(self, value):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            staff = User.objects.get(id=value, role="staff", is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Staff member not found.")
        if not staff.staff_profile.is_assignable:
            raise serializers.ValidationError("Staff member is unavailable for the selected time.")
        return staff


class CompletionSerializer(serializers.Serializer):
    remarks = serializers.CharField(required=False, allow_blank=True)
