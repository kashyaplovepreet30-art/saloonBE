from django.urls import path

from .views import (
    AddToCartView,
    CartView,
    ClearCartView,
    RemoveCartItemView,
    UpdateCartItemView,
)

urlpatterns = [
    path("", CartView.as_view(), name="cart"),
    path("add/", AddToCartView.as_view(), name="cart-add"),
    path("item/<int:item_id>/", UpdateCartItemView.as_view(), name="cart-item-update"),
    path("item/<int:item_id>/remove/", RemoveCartItemView.as_view(), name="cart-item-remove"),
    path("clear/", ClearCartView.as_view(), name="cart-clear"),
]
