from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.JobView.as_view(),
        name="job_list",
    ),
    path(
        "add/",
        views.AddJobView.as_view(),
        name="add_job",
    ),
    path(
        "<int:id>/update/",
        views.UpdateJobView.as_view(),
        name="update_job",
    ),
    path(
        "<int:id>/delete/",
        views.DeleteJobView.as_view(),
        name="delete_job",
    ),
]
