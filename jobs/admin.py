from django.contrib import admin
from .models import Job


class MyAdmin(admin.ModelAdmin):
    def save_model(self, request, instance, form, change):
        username = getattr(request.user, "username", "sys")
        instance = form.save(commit=False)
        instance.created_by = username
        instance.save()
        form.save_m2m()
        return instance


admin.site.register(Job, MyAdmin)
