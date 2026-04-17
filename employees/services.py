from employees.models import Employee


def sync_employee_from_applicant(applicant, username="sys"):
    if applicant.status != "hired":
        return None

    defaults = {
        "job": applicant.job,
        "employment_type": applicant.job.job_type if applicant.job else None,
        "date_started": applicant.date_applied.date() if applicant.date_applied else None,
        "is_active": True,
        "created_by": username,
        "updated_by": username,
    }

    employee, created = Employee.objects.get_or_create(
        applicant=applicant,
        defaults=defaults,
    )

    if created:
        return employee

    updated_fields = []
    if employee.job is None and applicant.job is not None:
        employee.job = applicant.job
        updated_fields.append("job")

    if employee.employment_type is None and applicant.job and applicant.job.job_type:
        employee.employment_type = applicant.job.job_type
        updated_fields.append("employment_type")

    if employee.date_started is None and applicant.date_applied:
        employee.date_started = applicant.date_applied.date()
        updated_fields.append("date_started")

    if not employee.is_active:
        employee.is_active = True
        updated_fields.append("is_active")

    employee.updated_by = username
    updated_fields.append("updated_by")

    if updated_fields:
        employee.save(update_fields=updated_fields)

    return employee
