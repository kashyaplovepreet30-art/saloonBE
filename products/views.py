from rest_framework import filters, parsers, viewsets

from common.permissions import IsAdminOrReadOnly
from products.models import Product
from products.serializers import ProductSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related("images").select_related("category").all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = (parsers.JSONParser, parsers.FormParser, parsers.MultiPartParser)
    search_fields = ("name", "sku", "brand", "description")
    ordering_fields = ("price", "created_at", "name")

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")
        status = self.request.query_params.get("status")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")

        if category:
            queryset = queryset.filter(category_id=category)
        if status:
            queryset = queryset.filter(status=status)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        if not self.request.user or not getattr(self.request.user, "is_authenticated", False):
            queryset = queryset.filter(status__in=["active", "out_of_stock"])
        return queryset
