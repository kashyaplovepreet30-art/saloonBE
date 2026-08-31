from django.conf import settings
from django.db import transaction
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.permissions import IsAdmin, IsCustomer
from payments import gateway
from payments.models import Payment, PaymentStatus
from payments.serializers import PaymentSerializer


class MyPaymentsView(generics.ListAPIView):
    permission_classes = [IsCustomer]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


class AdminPaymentListView(generics.ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = PaymentSerializer
    search_fields = ("transaction_id", "user__email")
    ordering_fields = ("created_at", "amount", "status")

    def get_queryset(self):
        queryset = Payment.objects.select_related("order", "appointment").all()
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


class AdminPaymentDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdmin]
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer


class GatewayConfigView(APIView):
    """Tells the browser whether a gateway is live, and which key to use."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "enabled": gateway.is_enabled(),
                "provider": "razorpay",
                "key_id": settings.RAZORPAY_KEY_ID if gateway.is_enabled() else "",
                "currency": settings.RAZORPAY_CURRENCY,
            }
        )


class CreateRazorpayOrderView(APIView):
    """Opens a Razorpay Order for a pending payment the customer owns."""

    permission_classes = [IsCustomer]

    def post(self, request):
        payment_id = request.data.get("payment")
        try:
            payment = Payment.objects.get(id=payment_id, user=request.user)
        except (Payment.DoesNotExist, TypeError, ValueError):
            return Response({"detail": "Payment not found."}, status=404)

        if payment.status == PaymentStatus.PAID:
            return Response({"detail": "This payment is already settled."}, status=400)

        if not gateway.is_enabled():
            return Response(
                {"detail": "Online payment is not available. The studio will collect payment directly."},
                status=503,
            )

        try:
            rp_order = gateway.create_order(
                payment.amount,
                receipt=payment.transaction_id,
                notes={"payment_id": str(payment.id), "user": request.user.email},
            )
        except gateway.GatewayError as exc:
            return Response({"detail": str(exc)}, status=502)

        payment.gateway_order_id = rp_order.get("id", "")
        payment.gateway_reference = rp_order.get("id", "")
        payment.save(update_fields=["gateway_order_id", "gateway_reference", "updated_at"])

        return Response(
            {
                "key_id": settings.RAZORPAY_KEY_ID,
                "razorpay_order_id": rp_order.get("id"),
                "amount": rp_order.get("amount"),
                "currency": rp_order.get("currency"),
                "payment": payment.id,
            }
        )


class VerifyRazorpayPaymentView(APIView):
    """Confirms a payment, but only if Razorpay's signature checks out."""

    permission_classes = [IsCustomer]

    @transaction.atomic
    def post(self, request):
        order_id = request.data.get("razorpay_order_id", "")
        rp_payment_id = request.data.get("razorpay_payment_id", "")
        signature = request.data.get("razorpay_signature", "")

        try:
            payment = Payment.objects.select_for_update().get(
                gateway_order_id=order_id, user=request.user
            )
        except Payment.DoesNotExist:
            return Response({"detail": "Payment not found."}, status=404)

        # The browser is not trusted: without a valid signature the payment is
        # marked failed rather than paid.
        if not gateway.verify_signature(order_id, rp_payment_id, signature):
            payment.status = PaymentStatus.FAILED
            payment.save(update_fields=["status", "updated_at"])
            return Response({"detail": "Payment signature could not be verified."}, status=400)

        payment.status = PaymentStatus.PAID
        payment.gateway_payment_id = rp_payment_id
        payment.gateway_signature = signature
        payment.save(
            update_fields=["status", "gateway_payment_id", "gateway_signature", "updated_at"]
        )

        # Keep the order's own payment_status in step.
        if payment.order:
            payment.order.payment_status = PaymentStatus.PAID
            payment.order.save(update_fields=["payment_status", "updated_at"])

        return Response(PaymentSerializer(payment).data)
