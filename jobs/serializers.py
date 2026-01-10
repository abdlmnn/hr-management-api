from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    job_type_name = serializers.SerializerMethodField()

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_job_type_name(self, obj):
        return obj.job_type.name if obj.job_type else None

    class Meta:
        model = Job
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "date_created",
        ]
