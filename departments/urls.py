from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.DepartmentView.as_view(),
        name="department_list",
    ),
    path(
        "add/",
        views.AddDepartmentView.as_view(),
        name="add_department",
    ),
    path(
        "<int:id>/update/",
        views.UpdateDepartmentView.as_view(),
        name="update_department",
    ),
    path(
        "<int:id>/delete/",
        views.DeleteDepartmentView.as_view(),
        name="delete_department",
    ),
]
