from rest_framework import serializers

from .models import Activity


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "date_created",
        ]

    def validate(self, attrs):
        start = attrs.get("when")
        if self.instance is not None and start is None:
            start = self.instance.when

        if "when_end" in attrs:
            end = attrs["when_end"]
        elif self.instance is not None:
            end = self.instance.when_end
        else:
            end = None

        if end is not None and start is not None and end < start:
            raise serializers.ValidationError(
                {"when_end": "End must be on or after the start time."}
            )
        return attrs

