from django.contrib import admin
from .models import EmailTemplate


class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "status")
    search_fields = ("name", "subject", "status")


admin.site.register(EmailTemplate, EmailTemplateAdmin)