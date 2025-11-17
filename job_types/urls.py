from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.JobTypeView.as_view(),
        name="job_type_list",
    ),
    path(
        "add/",
        views.AddJobTypeView.as_view(),
        name="add_job_type",
    ),
    path(
        "<int:id>/update/",
        views.UpdateJobTypeView.as_view(),
        name="update_job_type",
    ),
    path(
        "<int:id>/delete/",
        views.DeleteJobTypeView.as_view(),
        name="delete_job_type",
    ),
]
