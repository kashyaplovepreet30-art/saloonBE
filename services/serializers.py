from rest_framework import serializers

from .models import Service, ServiceCategory


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ("id", "name", "description", "image", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ServiceSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Service
        fields = (
            "id",
            "name",
            "category",
            "category_name",
            "description",
            "tagline",
            "gradient",
            "includes",
            "duration_minutes",
            "price",
            "discount",
            "image",
            "status",
            "required_staff",
            "final_price",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")
