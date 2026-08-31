from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ServiceCategoryViewSet, ServiceViewSet

router = DefaultRouter()
router.register("categories", ServiceCategoryViewSet, basename="service-category")
router.register("", ServiceViewSet, basename="service")

urlpatterns = [
    path("", include(router.urls)),
]
