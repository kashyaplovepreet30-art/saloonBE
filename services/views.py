from rest_framework import parsers, viewsets

from common.permissions import IsAdminOrReadOnly
from services.models import Service, ServiceCategory
from services.serializers import ServiceCategorySerializer, ServiceSerializer


class ServiceCategoryViewSet(viewsets.ModelViewSet):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ("name", "description")


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.select_related("category").all()
    serializer_class = ServiceSerializer
    permission_classes = [IsAdminOrReadOnly]
    parser_classes = (parsers.JSONParser, parsers.FormParser, parsers.MultiPartParser)
    search_fields = ("name", "description")
    ordering_fields = ("price", "created_at", "name")

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(category_id=category)
        if not self.request.user or not getattr(self.request.user, "is_authenticated", False):
            queryset = queryset.filter(status="active")
        return queryset
