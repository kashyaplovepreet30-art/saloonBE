from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import CustomerProfile


class CustomerProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    first_name = serializers.CharField(write_only=True, required=False)
    last_name = serializers.CharField(write_only=True, required=False)
    phone = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = CustomerProfile
        fields = (
            "id",
            "user",
            "address",
            "city",
            "state",
            "postal_code",
            "date_of_birth",
            "first_name",
            "last_name",
            "phone",
        )
        read_only_fields = ("id",)

    def update(self, instance, validated_data):
        user_data = {
            "first_name": validated_data.pop("first_name", instance.user.first_name),
            "last_name": validated_data.pop("last_name", instance.user.last_name),
            "phone": validated_data.pop("phone", instance.user.phone),
        }
        for attr, value in user_data.items():
            setattr(instance.user, attr, value)
        instance.user.save()
        return super().update(instance, validated_data)
