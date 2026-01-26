from django.urls import path
from jobs.views import PublicJobListView


urlpatterns = [
    path(
        "jobs/",
        PublicJobListView.as_view(),
        name="public_job_list",
    ),
]


