from rest_framework import serializers
from .models import Job


class JobSerializer(serializers.ModelSerializer):
    department_name = serializers.SerializerMethodField()
    job_type_name = serializers.SerializerMethodField()

    def get_department_name(self, obj):
        return obj.department.name if obj.department else None

    def get_job_type_name(self, obj):
        return obj.job_type.name if obj.job_type else None

    def _validate_string_array(self, value, field_name, max_items=50, max_length=200):
        """
        Helper method to validate a JSONField that should contain an array of strings.
        """
        if value is None:
            return []
        
        if not isinstance(value, list):
            raise serializers.ValidationError(f"{field_name} must be a list.")
        
        # Validate each item is a string and not empty
        validated_items = []
        for item in value:
            if not isinstance(item, str):
                raise serializers.ValidationError(f"Each {field_name} item must be a string.")
            item = item.strip()
            if not item:
                continue  # Skip empty strings
            if len(item) > max_length:
                raise serializers.ValidationError(
                    f"Each {field_name} item must be {max_length} characters or less."
                )
            validated_items.append(item)
        
        # Remove duplicates while preserving order (case-insensitive)
        seen = set()
        unique_items = []
        for item in validated_items:
            if item.lower() not in seen:
                seen.add(item.lower())
                unique_items.append(item)
        
        # Limit max items
        if len(unique_items) > max_items:
            raise serializers.ValidationError(f"Maximum {max_items} {field_name} allowed.")
        
        return unique_items

    def validate_requirements(self, value):
        """
        Validate that requirements is a list of strings.
        """
        return self._validate_string_array(
            value, 
            field_name="requirement",
            max_items=50,
            max_length=200
        )

    def validate_skills(self, value):
        """
        Validate that skills is a list of strings.
        """
        return self._validate_string_array(
            value,
            field_name="skill",
            max_items=50,
            max_length=100
        )

    class Meta:
        model = Job
        fields = "__all__"
        read_only_fields = [
            "created_by",
            "date_created",
        ]
