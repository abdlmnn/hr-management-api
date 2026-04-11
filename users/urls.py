from django.urls import path
from users.views import ChangePasswordView, ProfileView

urlpatterns = [
    path(
        "profile/",
        ProfileView.as_view(),
        name="profile",
    ),
    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change_password",
    ),
]
