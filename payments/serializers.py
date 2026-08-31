from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "transaction_id",
            "order",
            "appointment",
            "amount",
            "method",
            "status",
            "gateway_reference",
            "gateway_order_id",
            "gateway_payment_id",
            "created_at",
        )
        read_only_fields = ("id", "transaction_id", "created_at")
