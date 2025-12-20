from rest_framework import serializers
from .models import Department


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "date_created",
        ]

    def validate_name(self, value):
        if Department.objects.filter(name=value).exists():
            raise serializers.ValidationError("Department already exists")
        return value
