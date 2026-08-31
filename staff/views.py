from django.utils import timezone
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import RoleChoices
from common.permissions import IsAdmin, IsStaff, IsStaffOrAdmin
from staff.models import ItemRequest, RequestStatus, StaffProfile
from staff.serializers import (
    ItemRequestReviewSerializer,
    ItemRequestSerializer,
    StaffCreateSerializer,
    StaffProfileSerializer,
)


class StaffListView(generics.ListCreateAPIView):
    """Admin manages staff members."""

    permission_classes = [IsAdmin]
    queryset = StaffProfile.objects.select_related("user").all()
    search_fields = ("user__first_name", "user__last_name", "user__email", "department")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return StaffCreateSerializer
        return StaffProfileSerializer


class StaffDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdmin]
    queryset = StaffProfile.objects.select_related("user").all()
    serializer_class = StaffProfileSerializer


class StaffOwnProfileView(generics.RetrieveUpdateAPIView):
    """Staff member views/updates their own profile."""

    permission_classes = [IsStaff]
    serializer_class = StaffProfileSerializer

    def get_object(self):
        profile, _ = StaffProfile.objects.get_or_create(user=self.request.user)
        return profile


class ItemRequestListCreateView(generics.ListCreateAPIView):
    """Staff raise and see their own requests; admins see every request."""

    permission_classes = [IsStaffOrAdmin]
    serializer_class = ItemRequestSerializer
    search_fields = ("item", "reason", "staff__email")
    ordering_fields = ("created_at", "urgency", "status")

    def get_queryset(self):
        queryset = ItemRequest.objects.select_related("staff", "reviewed_by").all()
        if self.request.user.role != RoleChoices.ADMIN:
            queryset = queryset.filter(staff=self.request.user)
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset

    def perform_create(self, serializer):
        if self.request.user.role != RoleChoices.STAFF:
            raise PermissionDenied("Only staff members can raise item requests.")
        serializer.save(staff=self.request.user)


class ItemRequestReviewView(APIView):
    """Admin approves or rejects a pending request."""

    permission_classes = [IsAdmin]

    def post(self, request, pk):
        try:
            item_request = ItemRequest.objects.get(id=pk)
        except ItemRequest.DoesNotExist:
            return Response({"detail": "Item request not found."}, status=404)

        if item_request.status != RequestStatus.PENDING:
            return Response(
                {"detail": "This request has already been reviewed."}, status=400
            )

        serializer = ItemRequestReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        item_request.status = serializer.validated_data["status"]
        item_request.admin_notes = serializer.validated_data.get("admin_notes", "")
        item_request.reviewed_by = request.user
        item_request.reviewed_at = timezone.now()
        item_request.save()

        return Response(ItemRequestSerializer(item_request).data)
