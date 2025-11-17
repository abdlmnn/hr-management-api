from django.urls import path
from users.views import ChangePasswordView

urlpatterns = [
    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change_password",
    ),
]
