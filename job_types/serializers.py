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

    def validate_name(self, value):
      instance = self.instance
      qs = JobType.objects.filter(name=value)
      if instance:
          qs = qs.exclude(pk=instance.pk)
      if qs.exists():
          raise serializers.ValidationError("Job Type already exists")
      return value

