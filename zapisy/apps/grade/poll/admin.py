from django.contrib import admin

from .models import Poll, Submission, Schema


class SchemaAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        obj.user = request.user
        super().save_model(request, obj, form, change)


admin.site.register(Poll)
admin.site.register(Submission)
admin.site.register(Schema)
