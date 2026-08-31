from django.urls import path

from .views import (
    AdminPaymentDetailView,
    AdminPaymentListView,
    CreateRazorpayOrderView,
    GatewayConfigView,
    MyPaymentsView,
    VerifyRazorpayPaymentView,
)

urlpatterns = [
    path("my-payments/", MyPaymentsView.as_view(), name="my-payments"),
    path("config/", GatewayConfigView.as_view(), name="payment-gateway-config"),
    path("razorpay/create/", CreateRazorpayOrderView.as_view(), name="razorpay-create"),
    path("razorpay/verify/", VerifyRazorpayPaymentView.as_view(), name="razorpay-verify"),
    path("admin/", AdminPaymentListView.as_view(), name="admin-payments"),
    path("admin/<int:pk>/", AdminPaymentDetailView.as_view(), name="admin-payment-detail"),
]
