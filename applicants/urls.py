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
]
