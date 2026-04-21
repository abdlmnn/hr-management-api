import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from applicants.models import Applicant
from employees.models import Employee
from job_types.models import JobType
from jobs.models import Job


class EmployeeSerializer(serializers.ModelSerializer):
    applicant_id = serializers.IntegerField(source="applicant.id", read_only=True)
    full_name = serializers.CharField(source="applicant.full_name", required=True)
    email = serializers.EmailField(source="applicant.email", required=True)
    contact_number = serializers.CharField(source="applicant.contact_number", required=True)
    status = serializers.ChoiceField(source="applicant.status", choices=Applicant.STATUS_CHOICES, required=True)
    job_name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    department_name = serializers.SerializerMethodField()
    employment_type_name = serializers.SerializerMethodField()

    class Meta:
        model = Employee
        fields = [
            "id",
            "employee_id",
            "applicant",
            "applicant_id",
            "full_name",
            "email",
            "contact_number",
            "status",
            "job",
            "job_name",
            "department",
            "department_name",
            "employment_type",
            "employment_type_name",
            "date_started",
            "is_active",
            "date_created",
        ]
        read_only_fields = [
            "employee_id",
            "date_created",
            "department",
            "department_name",
            "job_name",
            "employment_type_name",
        ]
        extra_kwargs = {
            "applicant": {"read_only": True},
            "job": {"required": True},
            "employment_type": {"required": False, "allow_null": True},
        }

    def get_job_name(self, obj):
        return obj.job.name if obj.job else None

    def get_department(self, obj):
        return obj.job.department.id if obj.job and obj.job.department else None

    def get_department_name(self, obj):
        return obj.job.department.name if obj.job and obj.job.department else None

    def get_employment_type_name(self, obj):
        return obj.employment_type.name if obj.employment_type else None

    def update(self, instance, validated_data):
        applicant_data = validated_data.pop("applicant", {})
        username = validated_data.pop("updated_by", None) or getattr(self.context.get("request"), "user", None)
        username = getattr(username, "username", username) or "sys"

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if "job" in validated_data and validated_data.get("employment_type") is None and instance.employment_type is None and instance.job:
            instance.employment_type = instance.job.job_type

        instance.updated_by = username
        instance.save()

        applicant = instance.applicant
        applicant_updated_fields = []
        for attr, value in applicant_data.items():
            setattr(applicant, attr, value)
            applicant_updated_fields.append(attr)

        applicant.updated_by = username
        applicant_updated_fields.append("updated_by")
        applicant.save(update_fields=applicant_updated_fields)

        return instance


class CreateEmployeeSerializer(serializers.Serializer):
    """
    HR-only payload: creates a hired Applicant and provisions an Employee via signals.
    """

    full_name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    contact_number = serializers.CharField(max_length=100)
    job = serializers.PrimaryKeyRelatedField(queryset=Job.objects.filter(is_active=True))
    employment_type = serializers.PrimaryKeyRelatedField(queryset=JobType.objects.all())
    date_started = serializers.DateField()

    def validate_full_name(self, value):
        value = (value or "").strip()
        if not value:
            raise ValidationError("Full name is required.")
        if len(value) < 2:
            raise ValidationError("Full name must be at least 2 characters.")
        return value

    def validate_contact_number(self, value):
        value = (value or "").strip()
        if not value:
            raise ValidationError("Contact number is required.")

        normalized = re.sub(r"[\s\-()]", "", value)
        is_valid_ph_mobile = any(
            re.fullmatch(pattern, normalized)
            for pattern in (
                r"09\d{9}",
                r"\+639\d{9}",
                r"639\d{9}",
            )
        )

        if not is_valid_ph_mobile:
            raise ValidationError(
                "Contact number must be a valid Philippine mobile number, such as 09123456789 or +639123456789."
            )

        return value
