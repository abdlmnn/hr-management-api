from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Applicant
from datetime import timedelta
from django.utils import timezone


class ApplicantSerializer(serializers.ModelSerializer):
    valid_id = serializers.FileField(use_url=True, required=False)
    resume = serializers.FileField(use_url=True, required=False)
    job_name = serializers.SerializerMethodField()

    def validate(self, data):
        time_threshold = timezone.now() - timedelta(hours=24)

        applicant_exist = (
            Applicant.objects.filter(
                email__iexact=data.get("email"),
                job=data.get("job"),
                date_applied__gte=time_threshold,
            )
            .exclude(status="pending")
            .exists()
        )

        if applicant_exist:
            raise ValidationError(
                "You have already applied for this job, Please wait 24 hours"
            )

        return data

    def get_job_name(self, obj):
        return obj.job.name if obj.job else None

    def get_valid_id_url(self, obj):
        if obj.valid_id:
            return self.context["request"].build_absolute_uri(obj.valid_id.url)
        return None

    def get_resume_url(self, obj):
        if obj.resume:
            return self.context["request"].build_absolute_uri(obj.resume.url)
        return None

    class Meta:
        model = Applicant
        fields = [
            "full_name",
            "email",
            "contact_number",
            "job",
            "job_name",
            "cover_letter",
            "valid_id",
            "resume",
            "status",
            "date_applied",
        ]
        read_only_fields = (
            "verification_token",
            "token_created",
            "updated_by",
            "date_applied",
        )
        extra_kwargs = {
            "full_name": {"required": True},
            "email": {"required": True},
            "job": {"required": True},
        }
