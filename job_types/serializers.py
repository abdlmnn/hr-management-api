from rest_framework import serializers
from .models import JobType


class JobTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobType
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "date_created",
        ]
