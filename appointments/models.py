from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from payments.models import PaymentStatus
from services.models import Service


class AppointmentStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    ASSIGNED = "assigned", "Assigned"
    ACCEPTED = "accepted", "Accepted"
    IN_PROGRESS = "in_progress", "In Progress"
    COMPLETED = "completed", "Completed"
    CANCELLED = "cancelled", "Cancelled"
    REJECTED = "rejected", "Rejected"


class Appointment(models.Model):
    appointment_number = models.CharField(max_length=20, unique=True, blank=True)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="appointments",
        limit_choices_to={"role": "customer"},
    )
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="appointments")
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_appointments",
    )
    appointment_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField()
    customer_notes = models.TextField(blank=True, default="")
    admin_notes = models.TextField(blank=True, default="")
    completion_remarks = models.TextField(blank=True, default="")
    payment_status = models.CharField(
        max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING
    )
    status = models.CharField(
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("appointment_date", "start_time")

    def __str__(self):
        return self.appointment_number or f"Appointment #{self.id}"

    def overlaps(self, other):
        if self.appointment_date != other.appointment_date:
            return False
        return self.start_time < other.end_time and other.start_time < self.end_time


class AppointmentAssignment(models.Model):
    """History log of staff assignments for an appointment."""

    appointment = models.ForeignKey(
        Appointment, on_delete=models.CASCADE, related_name="assignments"
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="assignments"
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="assignments_made",
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes = models.CharField(max_length=200, blank=True, default="")

    def __str__(self):
        return f"{self.appointment} -> {self.staff.full_name}"


def create_appointment_number():
    return "APT-" + timezone.now().strftime("%Y%m%d%H%M%S")
