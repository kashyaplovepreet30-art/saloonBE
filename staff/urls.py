from django.urls import path

from .views import (
    ItemRequestListCreateView,
    ItemRequestReviewView,
    StaffDetailView,
    StaffListView,
    StaffOwnProfileView,
)

urlpatterns = [
    path("", StaffListView.as_view(), name="staff-list"),
    # Declared before the <int:pk> routes so the literal prefixes always win.
    path("requests/", ItemRequestListCreateView.as_view(), name="item-request-list"),
    path(
        "requests/<int:pk>/review/",
        ItemRequestReviewView.as_view(),
        name="item-request-review",
    ),
    path("me/", StaffOwnProfileView.as_view(), name="staff-own-profile"),
    path("<int:pk>/", StaffDetailView.as_view(), name="staff-detail"),
]
