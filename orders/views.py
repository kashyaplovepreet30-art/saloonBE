import uuid

from django.db import transaction
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response

from common.permissions import IsAdmin, IsCustomer
from carts.models import Cart
from carts.views import get_or_create_cart
from orders.models import Order, OrderItem, OrderStatus
from orders.serializers import CheckoutSerializer, OrderSerializer
from payments.models import Payment, PaymentMethod, PaymentStatus


class CheckoutView(APIView):
    permission_classes = [IsCustomer]

    @transaction.atomic
    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        cart = get_or_create_cart(request.user)
        if not cart.items.exists():
            return Response({"detail": "Your cart is empty."}, status=status.HTTP_400_BAD_REQUEST)

        subtotal = 0
        tax_amount = 0
        order_items_data = []

        for item in cart.items.select_related("product"):
            product = item.product
            if item.quantity > product.stock_quantity:
                return Response(
                    {
                        "detail": f"'{product.name}' is out of stock or quantity exceeds available stock."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            line_total = product.final_price * item.quantity
            tax = line_total * product.gst_tax / 100
            subtotal += line_total
            tax_amount += tax
            order_items_data.append(
                {
                    "product": product,
                    "product_name": product.name,
                    "quantity": item.quantity,
                    "unit_price": product.final_price,
                    "total_price": line_total + tax,
                }
            )

        discount_amount = 0
        total_amount = subtotal + tax_amount - discount_amount

        order = Order.objects.create(
            order_number="ORD-" + uuid.uuid4().hex[:10].upper(),
            customer=request.user,
            billing_address=serializer.validated_data.get("billing_address", ""),
            shipping_address=serializer.validated_data["shipping_address"],
            subtotal=subtotal,
            discount_amount=discount_amount,
            tax_amount=tax_amount,
            total_amount=total_amount,
            coupon_code=serializer.validated_data.get("coupon_code", ""),
            status=OrderStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
        )

        for data in order_items_data:
            product = data["product"]
            OrderItem.objects.create(order=order, **{k: v for k, v in data.items() if k != "product"})
            product.stock_quantity -= data["quantity"]
            product.save()

        payment = Payment.objects.create(
            user=request.user,
            order=order,
            amount=total_amount,
            method=serializer.validated_data["payment_method"],
            status=PaymentStatus.PENDING,
        )

        cart.items.all().delete()

        # The payment id is returned alongside the order so the client can hand
        # straight off to the gateway without having to look it up.
        data = OrderSerializer(order).data
        data["payment"] = payment.id
        return Response(data, status=status.HTTP_201_CREATED)


class MyOrdersView(generics.ListAPIView):
    permission_classes = [IsCustomer]
    serializer_class = OrderSerializer
    search_fields = ("order_number",)
    ordering_fields = ("created_at", "total_amount")

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user).prefetch_related("items")


class OrderDetailView(generics.RetrieveAPIView):
    permission_classes = [IsCustomer]
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(customer=self.request.user)


class AdminOrderListView(generics.ListAPIView):
    permission_classes = [IsAdmin]
    serializer_class = OrderSerializer
    search_fields = ("order_number", "customer__email", "customer__first_name")
    ordering_fields = ("created_at", "total_amount", "status")

    def get_queryset(self):
        queryset = Order.objects.select_related("customer").prefetch_related("items").all()
        status_filter = self.request.query_params.get("status")
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


class AdminOrderDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAdmin]
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_serializer_class(self):
        return OrderSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        data = request.data
        if "status" in data:
            instance.status = data["status"]
        if "payment_status" in data:
            instance.payment_status = data["payment_status"]
        instance.save()
        return Response(OrderSerializer(instance).data)
