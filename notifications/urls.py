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
    )
]
