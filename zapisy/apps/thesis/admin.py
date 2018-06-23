from django.contrib import admin

from . import models

admin.site.register(models.Thesis)
admin.site.register(models.ThesisCommissionMember)

class ThesisSystemSettingsAdmin(admin.ModelAdmin):
	def has_add_permission(self, request):
		return False

admin.site.register(models.ThesisSystemSettings, ThesisSystemSettingsAdmin)
