from datetime import date as date_cls, datetime, timedelta

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAdmin, IsCustomer, IsStaff
from services.models import Service
from staff.models import StaffProfile

from .models import (
    Appointment,
    AppointmentAssignment,
    AppointmentStatus,
)
from .serializers import (
    AppointmentSerializer,
    AssignStaffSerializer,
    BookAppointmentSerializer,
    CompletionSerializer,
)
from .utils import (
    generate_time_slots,
    get_available_staff,
    get_staff_overlap,
)


class AvailableSlotsView(APIView):
    """GET /api/appointments/slots/?service_id=&date=YYYY-MM-DD"""

    permission_classes = []

    def get(self, request):
        service_id = request.query_params.get("service_id")
        date_str = request.query_params.get("date")

        if not service_id or not date_str:
            return Response({"detail": "service_id and date are required."}, status=400)

        try:
            service = Service.objects.get(id=service_id, status="active")
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
        except (Service.DoesNotExist, ValueError):
            return Response({"detail": "Invalid service or date."}, status=400)

        slots = generate_time_slots(service, date)
        return Response({"date": date, "slots": slots})


class AvailableStaffView(APIView):
    """GET /api/appointments/available-staff/?service_id=&date=&start_time=HH:MM"""

    permission_classes = [IsAdmin]

    def get(self, request):
        service_id = request.query_params.get("service_id")
        date_str = request.query_params.get("date")
        start_str = request.query_params.get("start_time")

        try:
            service = Service.objects.get(id=service_id)
            date = datetime.strptime(date_str, "%Y-%m-%d").date()
            start_time = datetime.strptime(start_str, "%H:%M").time()
            end_time = (
                datetime.combine(date, start_time) + timedelta(minutes=service.duration_minutes)
            ).time()
        except (Service.DoesNotExist, ValueError, TypeError):
            return Response({"detail": "Invalid parameters."}, status=400)

        staff = get_available_staff(service, date, start_time, end_time)
        return Response({"staff": [s.staff_profile.id for s in staff]})


class BookAppointmentView(APIView):
    permission_classes = [IsCustomer]

    def post(self, request):
        serializer = BookAppointmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        appointment = Appointment.objects.create(
            appointment_number=datetime.now().strftime("APT%Y%m%d%H%M%S"),
            customer=request.user,
            service=serializer.validated_data["service"],
            appointment_date=serializer.validated_data["appointment_date"],
            start_time=serializer.validated_data["start_time"],
            end_time=serializer.validated_data["end_time"],
            duration_minutes=serializer.validated_data["duration_minutes"],
            customer_notes=serializer.validated_data.get("customer_notes", ""),
            status=AppointmentStatus.PENDING,
        )
        return Response(AppointmentSerializer(appointment).data, status=status.HTTP_201_CREATED)


class MyAppointmentsView(generics.ListAPIView):
    permission_classes = [IsCustomer]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.filter(customer=self.request.user).select_related(
            "service", "staff"
        )


class MyAppointmentDetailView(generics.RetrieveAPIView):
    permission_classes = [IsCustomer]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.filter(customer=self.request.user)


class CancelAppointmentView(APIView):
    permission_classes = [IsCustomer]

    def post(self, request, pk):
        try:
            appointment = Appointment.objects.get(id=pk, customer=request.user)
        except Appointment.DoesNotExist:
            return Response({"detail": "Appointment not found."}, status=404)

        cancellable = [
            AppointmentStatus.PENDING,
            AppointmentStatus.CONFIRMED,
            AppointmentStatus.ASSIGNED,
        ]
        if appointment.status not in cancellable:
            return Response(
                {"detail": "Appointment cannot be cancelled at this stage."}, status=400
            )

        appointment.status = AppointmentStatus.CANCELLED
        appointment.save()
        return Response(AppointmentSerializer(appointment).data)


class AdminAppointmentListView(generics.ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = AppointmentSerializer
    search_fields = ("appointment_number", "customer__email", "customer__first_name")
    ordering_fields = ("appointment_date", "start_time", "created_at")

    def get_queryset(self):
        queryset = Appointment.objects.select_related("customer", "service", "staff").all()
        status_filter = self.request.query_params.get("status")
        date_filter = self.request.query_params.get("date")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if date_filter:
            queryset = queryset.filter(appointment_date=date_filter)
        return queryset


class AdminAppointmentDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAdmin]
    queryset = Appointment.objects.select_related("customer", "service", "staff").all()
    serializer_class = AppointmentSerializer


class AssignStaffView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            appointment = Appointment.objects.get(id=pk)
        except Appointment.DoesNotExist:
            return Response({"detail": "Appointment not found."}, status=404)

        serializer = AssignStaffSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        staff = serializer.validated_data["staff_id"]

        conflict = get_staff_overlap(
            staff, appointment.appointment_date, appointment.start_time, appointment.end_time
        )
        if conflict:
            return Response(
                {
                    "detail": "Staff member has an overlapping appointment during the selected time."
                },
                status=400,
            )

        appointment.staff = staff
        if appointment.status == AppointmentStatus.PENDING:
            appointment.status = AppointmentStatus.CONFIRMED
        appointment.status = AppointmentStatus.ASSIGNED
        appointment.save()

        AppointmentAssignment.objects.create(
            appointment=appointment,
            staff=staff,
            assigned_by=request.user,
            notes=serializer.validated_data.get("notes", ""),
        )

        return Response(AppointmentSerializer(appointment).data)


class StaffAppointmentsView(generics.ListAPIView):
    permission_classes = [IsStaff]
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        queryset = Appointment.objects.filter(staff=self.request.user).select_related(
            "customer", "service"
        )
        view_type = self.request.query_params.get("view")

        if view_type == "today":
            queryset = queryset.filter(appointment_date=date_cls.today())
        elif view_type == "upcoming":
            queryset = queryset.filter(appointment_date__gte=date_cls.today()).exclude(
                status=AppointmentStatus.COMPLETED
            )
        return queryset


class StaffAppointmentActionView(APIView):
    """POST with action: accept | reject | start | complete"""

    permission_classes = [IsStaff]

    def post(self, request, pk, action):
        try:
            appointment = Appointment.objects.get(id=pk, staff=request.user)
        except Appointment.DoesNotExist:
            return Response({"detail": "Appointment not found."}, status=404)

        if action == "accept":
            if appointment.status != AppointmentStatus.ASSIGNED:
                return Response({"detail": "Only assigned appointments can be accepted."}, status=400)
            appointment.status = AppointmentStatus.ACCEPTED
        elif action == "reject":
            if appointment.status != AppointmentStatus.ASSIGNED:
                return Response({"detail": "Only assigned appointments can be rejected."}, status=400)
            appointment.status = AppointmentStatus.REJECTED
            appointment.staff = None
        elif action == "start":
            if appointment.status != AppointmentStatus.ACCEPTED:
                return Response({"detail": "Only accepted appointments can be started."}, status=400)
            appointment.status = AppointmentStatus.IN_PROGRESS
        elif action == "complete":
            if appointment.status != AppointmentStatus.IN_PROGRESS:
                return Response({"detail": "Only in-progress appointments can be completed."}, status=400)
            serializer = CompletionSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            appointment.completion_remarks = serializer.validated_data.get("remarks", "")
            appointment.status = AppointmentStatus.COMPLETED
        else:
            return Response({"detail": "Invalid action."}, status=400)

        appointment.save()
        return Response(AppointmentSerializer(appointment).data)
