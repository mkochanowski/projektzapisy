from django.contrib import admin

from . import models

admin.site.register(models.Thesis)
admin.site.register(models.ThesesCommissionMember)

class ThesesSystemSettingsAdmin(admin.ModelAdmin):
	def has_add_permission(self, request):
		return False

admin.site.register(models.ThesesSystemSettings, ThesesSystemSettingsAdmin)
