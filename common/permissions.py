from rest_framework.permissions import BasePermission

from accounts.models import RoleChoices


class IsAdmin(BasePermission):
    message = "Only administrators are allowed to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == RoleChoices.ADMIN
        )


class IsCustomer(BasePermission):
    message = "Only customers are allowed to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == RoleChoices.CUSTOMER
        )


class IsStaff(BasePermission):
    message = "Only staff members are allowed to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == RoleChoices.STAFF
        )


class IsAdminOrReadOnly(BasePermission):
    message = "Only administrators are allowed to modify this resource."

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == RoleChoices.ADMIN
        )


class IsCustomerOrAdminOrReadOnly(BasePermission):
    """Anyone may read; customers and admins may write.

    Used for reviews, where the writer is by definition a customer. The view's
    own perform_create still restricts creation to customers, and the serializer
    checks that the product was actually purchased or the service attended.
    """

    message = "Only customers can submit reviews."

    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in (RoleChoices.CUSTOMER, RoleChoices.ADMIN)
        )


class IsStaffOrAdmin(BasePermission):
    """Either role; the view narrows what each one actually sees."""

    message = "Only staff members and administrators are allowed to perform this action."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in (RoleChoices.STAFF, RoleChoices.ADMIN)
        )
