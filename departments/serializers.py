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
      instance = self.instance
      qs = Department.objects.filter(name=value)
      if instance:
          qs = qs.exclude(pk=instance.pk)
      if qs.exists():
          raise serializers.ValidationError("Department already exists")
      return value
