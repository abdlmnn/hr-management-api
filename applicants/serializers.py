from rest_framework import serializers
from .models import Applicant


class ApplicantSerializer(serializers.ModelSerializer):
    valid_id = serializers.FileField(
      use_url=True,
      required=False
    )
    resume = serializers.FileField(
      use_url=True,
      required=False
    )

    def get_valid_id_url(self, obj):
        if obj.valid_id:
            return self.context['request'].build_absolute_uri(obj.valid_id.url)
        return None

    def get_resume_url(self, obj):
        if obj.resume:
            return self.context['request'].build_absolute_uri(obj.resume.url)
        return None

    class Meta:
        model = Applicant
        fields = "__all__"
        read_only_fields = [
            "updated_by",
            "date_applied",
        ]
        xtra_kwargs = {
            'full_name': {'required': True},
            'email': {'required': True},
            'job': {'required': True},
        }
