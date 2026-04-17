from django.db import migrations, models
import django.db.models.deletion
import jobs.utils


def backfill_hired_applicants(apps, schema_editor):
    Applicant = apps.get_model("applicants", "Applicant")
    Employee = apps.get_model("employees", "Employee")

    hired_applicants = Applicant.objects.filter(status="hired").select_related("job", "job__job_type")
    for applicant in hired_applicants:
        employee, created = Employee.objects.get_or_create(
            applicant=applicant,
            defaults={
                "job": applicant.job,
                "employment_type": applicant.job.job_type if applicant.job else None,
                "date_started": applicant.date_applied.date() if applicant.date_applied else None,
                "is_active": True,
                "created_by": getattr(applicant, "updated_by", "sys") or "sys",
                "updated_by": getattr(applicant, "updated_by", "sys") or "sys",
            },
        )

        if not employee.employee_id:
            employee.employee_id = f"EMP-{employee.pk:06d}"
            employee.save(update_fields=["employee_id"])


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("applicants", "0008_auto_20260114_1423"),
        ("job_types", "0003_jobtype_updated_by"),
        ("jobs", "0003_add_skills_and_convert_requirements_to_json"),
    ]

    operations = [
        migrations.CreateModel(
            name="Employee",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("employee_id", models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ("date_started", models.DateField(blank=True, null=True)),
                ("is_active", models.BooleanField(default=True)),
                ("created_by", models.CharField(blank=True, default="sys", max_length=10, null=True)),
                ("updated_by", models.CharField(blank=True, default="sys", max_length=10, null=True)),
                ("date_created", models.DateTimeField(blank=True, default=jobs.utils.now, null=True)),
                (
                    "applicant",
                    models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="employee", to="applicants.applicant"),
                ),
                (
                    "employment_type",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="employees", to="job_types.jobtype"),
                ),
                (
                    "job",
                    models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="employees", to="jobs.job"),
                ),
            ],
            options={
                "verbose_name_plural": "Employees",
                "db_table": "employees",
                "ordering": ["-id"],
            },
        ),
        migrations.RunPython(backfill_hired_applicants, migrations.RunPython.noop),
    ]
