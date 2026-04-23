import os
import re

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Applicant, normalize_name_part


DERIVED_FULL_NAME_ERROR = (
    "full_name is derived from first_name, middle_name, and last_name. Send those fields instead."
)
PDF_ONLY_UPLOAD_ERROR = "Only PDF files are allowed."


class ApplicantNameWriteMixin:
    full_name = serializers.CharField(read_only=True)
    first_name = serializers.CharField(required=True, allow_blank=False, max_length=100)
    middle_name = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=100)
    last_name = serializers.CharField(required=True, allow_blank=False, max_length=100)

    def validate(self, attrs):
        if "full_name" in self.initial_data:
            raise ValidationError({"full_name": [DERIVED_FULL_NAME_ERROR]})
        return super().validate(attrs)

    def validate_first_name(self, value):
        value = normalize_name_part(value)
        if not value:
            raise ValidationError("First name is required.")
        return value

    def validate_middle_name(self, value):
        return normalize_name_part(value)

    def validate_last_name(self, value):
        value = normalize_name_part(value)
        if not value:
            raise ValidationError("Last name is required.")
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


class ApplicantUploadValidationMixin:
    def _max_upload_bytes(self) -> int:
        max_mb = int(os.getenv("APPLICANT_UPLOAD_MAX_MB", "25"))
        return max_mb * 1024 * 1024

    def _validate_pdf_upload(self, file_obj, field_name: str):
        if not file_obj:
            return
        file_name = (getattr(file_obj, "name", "") or "").lower()
        content_type = (getattr(file_obj, "content_type", "") or "").lower()
        if not file_name.endswith(".pdf"):
            raise ValidationError({field_name: [PDF_ONLY_UPLOAD_ERROR]})
        # Browsers/clients can omit content_type; only reject when it is present and clearly not PDF.
        if content_type and content_type != "application/pdf":
            raise ValidationError({field_name: [PDF_ONLY_UPLOAD_ERROR]})

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

    def _validate_upload(self, file_obj, field_name: str):
        self._validate_pdf_upload(file_obj, field_name)
        self._validate_upload_size(file_obj, field_name)

    def validate_valid_id(self, value):
        self._validate_upload(value, "valid_id")
        return value

    def validate_resume(self, value):
        self._validate_upload(value, "resume")
        return value


class ApplicantSerializer(ApplicantUploadValidationMixin, ApplicantNameWriteMixin, serializers.ModelSerializer):
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
            "first_name",
            "middle_name",
            "last_name",
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
            "full_name",
            "date_applied",
        )
        extra_kwargs = {
            "email": {"required": True},
            "job": {"required": True},
        }


class ApplicantCreateSerializer(ApplicantUploadValidationMixin, ApplicantNameWriteMixin, serializers.ModelSerializer):
    """
    Public-facing create serializer.
    Locks down server-controlled/internal fields so applicants cannot set them.
    """

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
            "first_name",
            "middle_name",
            "last_name",
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
            "full_name",
            "status",
            "date_applied",
        )
        extra_kwargs = {
            "job": {"required": True},
        }
