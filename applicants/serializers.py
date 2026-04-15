import os
import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .models import Applicant
from datetime import timedelta
from django.utils import timezone


class ApplicantSerializer(serializers.ModelSerializer):
    valid_id = serializers.FileField(use_url=True, required=False)
    resume = serializers.FileField(use_url=True, required=False)
    job_name = serializers.SerializerMethodField()

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
            "id",
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


class ApplicantCreateSerializer(serializers.ModelSerializer):
    """
    Public-facing create serializer.
    Locks down server-controlled/internal fields so applicants cannot set them.
    """

    full_name = serializers.CharField(required=True, allow_blank=False, max_length=100)
    email = serializers.EmailField(required=True, allow_blank=False)
    contact_number = serializers.CharField(required=True, allow_blank=False, max_length=30)
    valid_id = serializers.FileField(use_url=True, required=False)
    resume = serializers.FileField(use_url=True, required=False)
    job_name = serializers.SerializerMethodField()
    captcha_token = serializers.CharField(write_only=True, required=False)

    def get_job_name(self, obj):
        return obj.job.name if obj.job else None

    class Meta:
        model = Applicant
        fields = [
            "id",
            "full_name",
            "email",
            "contact_number",
            "job",
            "job_name",
            "cover_letter",
            "valid_id",
            "resume",
            "captcha_token",
            "status",
            "date_applied",
        ]
        read_only_fields = (
            # Server-controlled fields
            "status",
            "date_applied",
        )
        extra_kwargs = {
            "job": {"required": True},
        }

    def validate_full_name(self, value: str) -> str:
        value = (value or "").strip()
        if not value:
            raise ValidationError("Full name is required.")
        if len(value) < 2:
            raise ValidationError("Full name must be at least 2 characters.")
        return value

    def validate_contact_number(self, value: str) -> str:
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

    def _max_upload_bytes(self) -> int:

        max_mb = int(os.getenv("APPLICANT_UPLOAD_MAX_MB", "25"))
        return max_mb * 1024 * 1024

    def _validate_upload_size(self, file_obj, field_name: str):
        if not file_obj:
            return
        size = getattr(file_obj, "size", None)
        if size is None:
            return
        max_bytes = self._max_upload_bytes()
        if size > max_bytes:
            max_mb = max_bytes // (1024 * 1024)
            raise ValidationError({field_name: [f"File is too large. Maximum size is {max_mb} MB."]})

    def validate_valid_id(self, value):
        self._validate_upload_size(value, "valid_id")
        return value

    def validate_resume(self, value):
        self._validate_upload_size(value, "resume")
        return value
