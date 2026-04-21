from django.contrib import admin

from employees.models import Employee


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("employee_id", "applicant", "job", "employment_type", "date_started", "is_active")
    search_fields = (
        "employee_id",
        "applicant__full_name",
        "applicant__first_name",
        "applicant__middle_name",
        "applicant__last_name",
        "applicant__email",
        "job__name",
    )
    list_filter = ("is_active", "employment_type")

    def save_model(self, request, obj, form, change):
        username = getattr(request.user, "username", "sys")
        if not obj.pk and not obj.created_by:
            obj.created_by = username
        obj.updated_by = username
        super().save_model(request, obj, form, change)


admin.site.register(Employee, EmployeeAdmin)
