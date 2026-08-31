from django.urls import path

from .views import (
    MarkAllReadView,
    MarkReadView,
    MyNotificationsView,
    UnreadCountView,
)

urlpatterns = [
    path("", MyNotificationsView.as_view(), name="my-notifications"),
    path("unread-count/", UnreadCountView.as_view(), name="unread-count"),
    path("mark-all-read/", MarkAllReadView.as_view(), name="mark-all-read"),
    path("<int:pk>/mark-read/", MarkReadView.as_view(), name="mark-read"),
]
