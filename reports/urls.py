from django.urls import path

from .views import (
    AppointmentReportView,
    DashboardView,
    OrderReportView,
    ProductReportView,
    RevenueReportView,
    StaffReportView,
)

urlpatterns = [
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("revenue/", RevenueReportView.as_view(), name="revenue-report"),
    path("orders/", OrderReportView.as_view(), name="order-report"),
    path("appointments/", AppointmentReportView.as_view(), name="appointment-report"),
    path("products/", ProductReportView.as_view(), name="product-report"),
    path("staff/", StaffReportView.as_view(), name="staff-report"),
]
