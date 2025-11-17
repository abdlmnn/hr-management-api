from django.urls import path
from . import views

urlpatterns = [
    path(
        "add/",
        views.AddEmailNotificationView.as_view(),
        name="add_email_notification",
    ),
]
