from rest_framework import serializers

from orders.models import Order, OrderStatus
from appointments.models import Appointment, AppointmentStatus

from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)

    class Meta:
        model = Review
        fields = ("id", "customer", "customer_name", "product", "service", "rating", "comment", "created_at")
        read_only_fields = ("id", "customer", "created_at")

    def validate(self, attrs):
        product = attrs.get("product") or getattr(self.instance, "product", None)
        service = attrs.get("service") or getattr(self.instance, "service", None)

        if not product and not service:
            raise serializers.ValidationError("A review must reference a product or a service.")
        if product and service:
            raise serializers.ValidationError("A review cannot reference both a product and a service.")

        user = self.context["request"].user

        # The model's UniqueConstraints cover (customer, product) and
        # (customer, service), but DRF cannot evaluate the generated validators
        # because `customer` is read-only and injected in perform_create. Without
        # this check a second review hits the database constraint directly and
        # surfaces as a 500 rather than a validation error.
        if self.instance is None:
            duplicate = Review.objects.filter(customer=user)
            duplicate = (
                duplicate.filter(product=product) if product else duplicate.filter(service=service)
            )
            if duplicate.exists():
                raise serializers.ValidationError(
                    "You have already reviewed this."
                    if product
                    else "You have already reviewed this service."
                )

        if product:
            purchased = Order.objects.filter(
                customer=user,
                status__in=[OrderStatus.DELIVERED, OrderStatus.COMPLETED],
                items__product=product,
            ).exists()
            if not purchased:
                raise serializers.ValidationError(
                    {"product": "You can only review products you have purchased."}
                )
        elif service:
            attended = Appointment.objects.filter(
                customer=user,
                service=service,
                status=AppointmentStatus.COMPLETED,
            ).exists()
            if not attended:
                raise serializers.ValidationError(
                    {"service": "You can only review services you have completed."}
                )
        return attrs
