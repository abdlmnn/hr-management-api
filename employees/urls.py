from django.urls import path

from . import views


urlpatterns = [
    path("", views.EmployeeView.as_view(), name="employee_list"),
    path("<int:id>/", views.RetrieveEmployeeView.as_view(), name="retrieve_employee"),
    path("<int:id>/update/", views.UpdateEmployeeView.as_view(), name="update_employee"),
]
