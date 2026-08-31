from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from common.permissions import IsCustomer
from products.models import Product

from .models import Cart, CartItem
from .serializers import CartItemSerializer, CartSerializer


def get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(customer=user)
    return cart


class CartView(APIView):
    permission_classes = [IsCustomer]

    def get(self, request):
        cart = get_or_create_cart(request.user)
        return Response(CartSerializer(cart).data)


class AddToCartView(APIView):
    permission_classes = [IsCustomer]

    def post(self, request):
        cart = get_or_create_cart(request.user)
        serializer = CartItemSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data["product"]
        quantity = serializer.validated_data.get("quantity", 1)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={"quantity": quantity},
        )
        if not created:
            item.quantity = min(item.quantity + quantity, product.stock_quantity)
            item.save()

        return Response(CartSerializer(cart).data, status=status.HTTP_200_OK)


class UpdateCartItemView(APIView):
    permission_classes = [IsCustomer]

    def patch(self, request, item_id):
        cart = get_or_create_cart(request.user)
        try:
            item = cart.items.get(id=item_id)
        except CartItem.DoesNotExist:
            return Response({"detail": "Cart item not found."}, status=404)

        serializer = CartItemSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(CartSerializer(cart).data)


class RemoveCartItemView(APIView):
    permission_classes = [IsCustomer]

    def delete(self, request, item_id):
        cart = get_or_create_cart(request.user)
        try:
            item = cart.items.get(id=item_id)
        except CartItem.DoesNotExist:
            return Response({"detail": "Cart item not found."}, status=404)
        item.delete()
        return Response(CartSerializer(cart).data)


class ClearCartView(APIView):
    permission_classes = [IsCustomer]

    def delete(self, request):
        cart = get_or_create_cart(request.user)
        cart.items.all().delete()
        return Response({"detail": "Cart cleared."})
