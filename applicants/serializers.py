from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Applicant


class ApplicantSerializer(serializers.ModelSerializer):
    valid_id = serializers.FileField(use_url=True, required=False)
    resume = serializers.FileField(use_url=True, required=False)
    job_name = serializers.SerializerMethodField()

    def validate(self, data):
        email = data.get("email")
        job = data.get("job")

        if Applicant.objects.filter(
            email__iexact=email, job=job, status__in=["pending", "applied"]
        ).exists():
            raise ValidationError("You have already applied for this job")

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
        fields = "__all__"
        read_only_fields = [
            "updated_by",
            "date_applied",
        ]
        extra_kwargs = {
            "full_name": {"required": True},
            "email": {"required": True},
            "job": {"required": True},
        }
