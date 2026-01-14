from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.ApplicantView.as_view(),
        name="applicant_list",
    ),
    path(
        "add/",
        views.AddApplicantView.as_view(),
        name="add_applicant",
    ),
    path(
        "<int:id>/update/",
        views.UpdateApplicantView.as_view(),
        name="update_applicant",
    ),
    path(
        "<int:id>/delete/",
        views.DeleteApplicantView.as_view(),
        name="delete_applicant",
    ),
    path(
        "pending-status/",
        views.PendingApplicantView.as_view(),
        name="pending_applicant",
    ),
    path(
        "<str:token>/verify/",
        views.VerifyApplicantView.as_view(),
        name="verify_applicant",
    ),
]
