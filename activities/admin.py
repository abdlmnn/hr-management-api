from django.contrib import admin

from .models import Activity


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ("what", "where", "when", "when_end", "created_by", "updated_by", "date_created")
    list_filter = ("when",)
    search_fields = ("what", "where", "note")
    ordering = ("-id",)

    def save_model(self, request, obj, form, change):
        username = getattr(request.user, "username", "sys")
        if change:
            obj.updated_by = username
        else:
            obj.created_by = username
        super().save_model(request, obj, form, change)
