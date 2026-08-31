from rest_framework import serializers

from accounts.models import RoleChoices, User

from .models import ItemRequest, RequestStatus, StaffProfile, StaffStatus


class StaffUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "phone", "profile_image", "is_active")


class StaffProfileSerializer(serializers.ModelSerializer):
    user = StaffUserSerializer(read_only=True)

    class Meta:
        model = StaffProfile
        fields = (
            "id",
            "user",
            "department",
            "skills",
            "experience_years",
            "status",
            "joining_date",
            "is_assignable",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class StaffCreateSerializer(serializers.Serializer):
    """Admin-only serializer to create a new staff account."""

    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    phone = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
    department = serializers.CharField(required=False, allow_blank=True)
    skills = serializers.CharField(required=False, allow_blank=True)
    experience_years = serializers.IntegerField(min_value=0, default=0)
    status = serializers.ChoiceField(choices=StaffStatus.choices)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value.lower()

    def create(self, validated_data):
        password = validated_data.pop("password")
        email = validated_data.pop("email")
        user = User.objects.create_user(username=email, email=email, password=password)
        user.role = RoleChoices.STAFF
        user.first_name = validated_data.pop("first_name")
        user.last_name = validated_data.pop("last_name")
        user.phone = validated_data.pop("phone", "")
        user.save()
        return StaffProfile.objects.create(user=user, **validated_data)


class ItemRequestSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source="staff.full_name", read_only=True)
    reviewed_by_name = serializers.CharField(
        source="reviewed_by.full_name", read_only=True, default=None
    )

    class Meta:
        model = ItemRequest
        fields = (
            "id",
            "staff",
            "staff_name",
            "item",
            "quantity",
            "reason",
            "urgency",
            "status",
            "admin_notes",
            "reviewed_by",
            "reviewed_by_name",
            "reviewed_at",
            "created_at",
        )
        # A requester sets item/quantity/reason/urgency; everything else is
        # decided by the admin review flow.
        read_only_fields = (
            "id",
            "staff",
            "status",
            "admin_notes",
            "reviewed_by",
            "reviewed_at",
            "created_at",
        )


class ItemRequestReviewSerializer(serializers.Serializer):
    """Admin decision on a pending request."""

    status = serializers.ChoiceField(
        choices=[RequestStatus.APPROVED, RequestStatus.REJECTED]
    )
    admin_notes = serializers.CharField(required=False, allow_blank=True)
