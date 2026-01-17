from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.EmailTemplateView.as_view(),
        name="email_template_list",
    ),
    path(
        "add/",
        views.AddEmailTemplateView.as_view(),
        name="add_email_template",
    ),
    path(
        "<int:id>/",
        views.RetrieveEmailTemplateView.as_view(),
        name="retrieve_email_template",
    ),
    path(
        "<int:id>/update/",
        views.UpdateEmailTemplateView.as_view(),
        name="update_email_template",
    ),
    path(
        "<int:id>/delete/",
        views.DeleteEmailTemplateView.as_view(),
        name="delete_email_template",
    ),
]
