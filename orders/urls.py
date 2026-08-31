from django.urls import path

from .views import (
    AdminOrderDetailView,
    AdminOrderListView,
    CheckoutView,
    MyOrdersView,
    OrderDetailView,
)

urlpatterns = [
    path("checkout/", CheckoutView.as_view(), name="checkout"),
    path("my-orders/", MyOrdersView.as_view(), name="my-orders"),
    path("my-orders/<int:pk>/", OrderDetailView.as_view(), name="order-detail"),
    path("admin/", AdminOrderListView.as_view(), name="admin-orders"),
    path("admin/<int:pk>/", AdminOrderDetailView.as_view(), name="admin-order-detail"),
]
