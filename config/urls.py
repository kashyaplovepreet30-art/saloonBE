"""
URL configuration for the Salon E-Commerce & Service Booking Platform.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def api_root(request):
    return JsonResponse({"message": "Salon backend is running"})


urlpatterns = [
    path("", api_root),
    path("admin/", admin.site.urls),
    path("api/auth/", include("accounts.urls")),
    path("api/customers/", include("customers.urls")),
    path("api/staff/", include("staff.urls")),
    path("api/categories/", include("categories.urls")),
    path("api/products/", include("products.urls")),
    path("api/services/", include("services.urls")),
    path("api/cart/", include("carts.urls")),
    path("api/orders/", include("orders.urls")),
    path("api/appointments/", include("appointments.urls")),
    path("api/payments/", include("payments.urls")),
    path("api/reviews/", include("reviews.urls")),
    path("api/notifications/", include("notifications.urls")),
    # Mounted under its own prefix. At the bare "api/" prefix the report routes
    # for products/ and staff/ were shadowed by the products and staff apps
    # above (both register a list view at their root), making those two reports
    # unreachable.
    path("api/reports/", include("reports.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
