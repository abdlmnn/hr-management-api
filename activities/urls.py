from django.urls import path

from . import views


urlpatterns = [
    path("", views.ActivityView.as_view(), name="activity_list"),
    path("add/", views.AddActivityView.as_view(), name="add_activity"),
    path("<int:id>/", views.RetrieveActivityView.as_view(), name="retrieve_activity"),
    path("<int:id>/update/", views.UpdateActivityView.as_view(), name="update_activity"),
    path("<int:id>/delete/", views.DeleteActivityView.as_view(), name="delete_activity"),
]

