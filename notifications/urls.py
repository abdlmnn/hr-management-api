from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.ListEmailNotificationsView.as_view(),
        name="list_email_notifications",
    ),
    path(
        "add/",
        views.AddEmailNotificationView.as_view(),
        name="add_email_notification",
    ),
    path(
        "<int:id>/",
        views.EmailNotificationDetailView.as_view(),
        name="email_notification_detail",
    ),
    path(
        "<int:id>/update/",
        views.EmailNotificationDetailView.as_view(),
        name="update_email_notification_detail",
    ),
    path(
        "<int:id>/delete/",
        views.EmailNotificationDetailView.as_view(),
        name="delete_email_notification_detail",
    ),
]
