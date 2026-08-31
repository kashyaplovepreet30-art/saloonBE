from rest_framework import generics
from rest_framework.exceptions import PermissionDenied

from common.permissions import IsAdminOrReadOnly, IsCustomer, IsCustomerOrAdminOrReadOnly
from reviews.models import Review
from reviews.serializers import ReviewSerializer


class ReviewListCreateView(generics.ListCreateAPIView):
    # Reviews are written by customers, so IsAdminOrReadOnly would reject the
    # only people the view is for — perform_create below is the real guard.
    permission_classes = [IsCustomerOrAdminOrReadOnly]
    serializer_class = ReviewSerializer
    search_fields = ("comment", "customer__email")

    def get_queryset(self):
        queryset = Review.objects.select_related("customer").all()
        product_id = self.request.query_params.get("product")
        service_id = self.request.query_params.get("service")
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        if service_id:
            queryset = queryset.filter(service_id=service_id)
        return queryset

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated or self.request.user.role != "customer":
            raise PermissionDenied("Only customers can submit reviews.")
        serializer.save(customer=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.select_related("customer").all()
    serializer_class = ReviewSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsAdminOrReadOnly()]
        return [IsCustomer()]

    def get_queryset(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return Review.objects.filter(customer=self.request.user)
        return super().get_queryset()
