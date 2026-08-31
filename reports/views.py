from datetime import date, timedelta

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAdmin
from appointments.models import Appointment, AppointmentStatus
from orders.models import Order, OrderStatus
from payments.models import Payment, PaymentStatus
from products.models import Product
from services.models import Service


def _count_role(role):
    from django.contrib.auth import get_user_model

    return get_user_model().objects.filter(role=role).count()


class DashboardView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        today = timezone.localdate()
        completed_statuses = [OrderStatus.DELIVERED, OrderStatus.COMPLETED]
        revenue = Payment.objects.filter(status=PaymentStatus.PAID).aggregate(
            total=Sum("amount")
        )["total"] or 0

        data = {
            "total_customers": _count_role("customer"),
            "total_staff": _count_role("staff"),
            "total_products": Product.objects.count(),
            "total_services": Service.objects.count(),
            "todays_appointments": Appointment.objects.filter(appointment_date=today).count(),
            "pending_appointments": Appointment.objects.filter(
                status=AppointmentStatus.PENDING
            ).count(),
            "completed_appointments": Appointment.objects.filter(
                status=AppointmentStatus.COMPLETED
            ).count(),
            "total_orders": Order.objects.count(),
            "pending_orders": Order.objects.filter(status=OrderStatus.PENDING).count(),
            "total_revenue": revenue,
            "recent_orders": list(
                Order.objects.values("id", "order_number", "total_amount", "status", "created_at")
                .order_by("-created_at")[:5]
            ),
            "recent_appointments": list(
                Appointment.objects.values(
                    "id", "appointment_number", "appointment_date", "start_time", "status"
                ).order_by("-created_at")[:5]
            ),
            "best_selling_products": list(
                Order.objects.filter(status__in=completed_statuses)
                .values("items__product__name")
                .annotate(total_sold=Sum("items__quantity"))
                .order_by("-total_sold")[:5]
            ),
            "popular_services": list(
                Appointment.objects.filter(status=AppointmentStatus.COMPLETED)
                .values("service__name")
                .annotate(count=Count("id"))
                .order_by("-count")[:5]
            ),
        }
        return Response(data)


class RevenueReportView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        days = int(request.query_params.get("days", 30))
        start_date = date.today() - timedelta(days=days - 1)

        daily = (
            Payment.objects.filter(status=PaymentStatus.PAID, created_at__date__gte=start_date)
            .extra({"day": "DATE(created_at)"})
            .values("day")
            .annotate(revenue=Sum("amount"))
            .order_by("day")
        )

        product_revenue = (
            Order.objects.filter(status__in=[OrderStatus.DELIVERED, OrderStatus.COMPLETED])
            .aggregate(total=Sum("total_amount"))["total"]
            or 0
        )
        service_revenue = (
            Payment.objects.filter(
                status=PaymentStatus.PAID, appointment__isnull=False
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        return Response(
            {
                "period_days": days,
                "daily": list(daily),
                "product_revenue": product_revenue,
                "service_revenue": service_revenue,
                "total_revenue": product_revenue + service_revenue,
            }
        )


class OrderReportView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(
            {
                "total_orders": Order.objects.count(),
                "pending": Order.objects.filter(status=OrderStatus.PENDING).count(),
                "completed": Order.objects.filter(
                    status__in=[OrderStatus.DELIVERED, OrderStatus.COMPLETED]
                ).count(),
                "cancelled": Order.objects.filter(status=OrderStatus.CANCELLED).count(),
            }
        )


class AppointmentReportView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(
            {
                "total_appointments": Appointment.objects.count(),
                "pending": Appointment.objects.filter(status=AppointmentStatus.PENDING).count(),
                "completed": Appointment.objects.filter(status=AppointmentStatus.COMPLETED).count(),
                "cancelled": Appointment.objects.filter(status=AppointmentStatus.CANCELLED).count(),
            }
        )


class ProductReportView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        return Response(
            {
                "out_of_stock": Product.objects.filter(stock_quantity=0).count(),
                "low_stock": Product.objects.filter(stock_quantity__lte=5).count(),
                "best_sellers": list(
                    Order.objects.filter(
                        status__in=[OrderStatus.DELIVERED, OrderStatus.COMPLETED]
                    )
                    .values("items__product__name")
                    .annotate(total_sold=Sum("items__quantity"))
                    .order_by("-total_sold")[:10]
                ),
            }
        )


class StaffReportView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        staff_report = []
        for staff in Appointment.objects.exclude(staff=None).values("staff__email", "staff__first_name").distinct():
            staff_report.append(
                {
                    "staff": staff["staff__first_name"],
                    "email": staff["staff__email"],
                    "completed": Appointment.objects.filter(
                        staff__email=staff["staff__email"], status=AppointmentStatus.COMPLETED
                    ).count(),
                    "cancelled": Appointment.objects.filter(
                        staff__email=staff["staff__email"], status=AppointmentStatus.CANCELLED
                    ).count(),
            }
        )
        return Response(staff_report)
