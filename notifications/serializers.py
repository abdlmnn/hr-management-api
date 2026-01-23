from rest_framework import serializers
from .models import EmailNotification


class EmailNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmailNotification
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "date_created",
            "error_message",
            "retry_count",
            "last_attempt",
        ]
