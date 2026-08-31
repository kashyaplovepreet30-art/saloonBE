from django.urls import path

from .views import (
    AdminAppointmentDetailView,
    AdminAppointmentListView,
    AssignStaffView,
    AvailableSlotsView,
    AvailableStaffView,
    BookAppointmentView,
    CancelAppointmentView,
    MyAppointmentDetailView,
    MyAppointmentsView,
    StaffAppointmentActionView,
    StaffAppointmentsView,
)

urlpatterns = [
    path("slots/", AvailableSlotsView.as_view(), name="appointment-slots"),
    path("available-staff/", AvailableStaffView.as_view(), name="appointment-available-staff"),
    path("book/", BookAppointmentView.as_view(), name="appointment-book"),
    path("my-appointments/", MyAppointmentsView.as_view(), name="my-appointments"),
    path("my-appointments/<int:pk>/", MyAppointmentDetailView.as_view(), name="appointment-detail"),
    path("my-appointments/<int:pk>/cancel/", CancelAppointmentView.as_view(), name="appointment-cancel"),
    path("staff/", StaffAppointmentsView.as_view(), name="staff-appointments"),
    path("staff/<int:pk>/<str:action>/", StaffAppointmentActionView.as_view(), name="staff-appointment-action"),
    path("admin/", AdminAppointmentListView.as_view(), name="admin-appointments"),
    path("admin/<int:pk>/", AdminAppointmentDetailView.as_view(), name="admin-appointment-detail"),
    path("admin/<int:pk>/assign/", AssignStaffView.as_view(), name="appointment-assign"),
]
