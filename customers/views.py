from rest_framework import generics

from common.permissions import IsCustomer
from customers.models import CustomerProfile
from customers.serializers import CustomerProfileSerializer


class CustomerProfileView(generics.RetrieveUpdateAPIView):
    """Retrieve or update the authenticated customer's own profile."""

    serializer_class = CustomerProfileSerializer
    permission_classes = [IsCustomer]

    def get_object(self):
        profile, _ = CustomerProfile.objects.get_or_create(user=self.request.user)
        return profile
