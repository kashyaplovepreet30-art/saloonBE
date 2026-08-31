"""Appointment scheduling helpers (slot generation, conflict checks)."""
from datetime import datetime, timedelta

from django.conf import settings

from staff.models import StaffStatus


def parse_business_hours():
    opening = datetime.strptime(settings.SALON_OPENING_TIME, "%H:%M").time()
    closing = datetime.strptime(settings.SALON_CLOSING_TIME, "%H:%M").time()
    return opening, closing


def get_studio_capacity():
    """How many staff the studio can put on the floor at once."""
    from django.contrib.auth import get_user_model

    User = get_user_model()
    return User.objects.filter(
        role="staff",
        is_active=True,
        staff_profile__status=StaffStatus.AVAILABLE,
    ).count()


def generate_time_slots(service, date):
    """Return list of {start, end, available} dicts for a service on a date.

    Slots respect salon operating hours and the service duration. Availability
    is a capacity question, not a yes/no one: a slot stays open while the staff
    already committed to overlapping appointments, plus the staff this service
    needs, still fit within the studio's capacity.

    (Previously any single overlapping appointment closed the slot for
    everyone, so a studio with several staff could still only ever run one
    appointment at a time.)
    """
    from .models import Appointment, AppointmentStatus

    opening, closing = parse_business_hours()
    duration = timedelta(minutes=service.duration_minutes)

    slots = []
    cursor = datetime.combine(date, opening)
    closing_dt = datetime.combine(date, closing)

    while cursor + duration <= closing_dt:
        slot_end = cursor + duration
        slots.append(
            {
                "start": cursor.time(),
                "end": slot_end.time(),
            }
        )
        cursor += timedelta(minutes=30)

    active_statuses = [
        AppointmentStatus.PENDING,
        AppointmentStatus.CONFIRMED,
        AppointmentStatus.ASSIGNED,
        AppointmentStatus.ACCEPTED,
        AppointmentStatus.IN_PROGRESS,
    ]

    capacity = get_studio_capacity()
    needed = max(1, service.required_staff or 1)

    # Fetched once rather than per slot.
    booked = list(
        Appointment.objects.filter(
            appointment_date=date,
            status__in=active_statuses,
        ).select_related("service")
    )

    for slot in slots:
        committed = 0
        for appointment in booked:
            if slot["start"] < appointment.end_time and appointment.start_time < slot["end"]:
                committed += max(1, getattr(appointment.service, "required_staff", 1) or 1)
        slot["available"] = capacity > 0 and committed + needed <= capacity

    return slots


def get_staff_overlap(staff, date, start_time, end_time, exclude_appointment=None):
    """Return the first overlapping active appointment for staff, if any."""
    from .models import Appointment, AppointmentStatus

    active_statuses = [
        AppointmentStatus.ASSIGNED,
        AppointmentStatus.ACCEPTED,
        AppointmentStatus.IN_PROGRESS,
    ]
    queryset = Appointment.objects.filter(
        staff=staff,
        appointment_date=date,
        status__in=active_statuses,
    )
    if exclude_appointment:
        queryset = queryset.exclude(id=exclude_appointment.id)

    for appointment in queryset:
        if start_time < appointment.end_time and appointment.start_time < end_time:
            return appointment
    return None


def get_available_staff(service, date, start_time, end_time):
    """Return staff who can take the appointment (available + no conflict)."""
    from django.contrib.auth import get_user_model
    from .models import AppointmentStatus
    from staff.models import StaffProfile

    User = get_user_model()
    staff_members = User.objects.filter(
        role="staff",
        is_active=True,
        staff_profile__status=StaffStatus.AVAILABLE,
    ).select_related("staff_profile")

    available = []
    for staff in staff_members:
        conflict = get_staff_overlap(staff, date, start_time, end_time)
        if not conflict:
            available.append(staff)
    return available
