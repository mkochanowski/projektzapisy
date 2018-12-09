from django.contrib import admin

from . import models, forms


class ThesisAdmin(admin.ModelAdmin):
    form = forms.ThesisForm


admin.site.register(models.Thesis, ThesisAdmin)


admin.site.register(models.ThesesBoardMember)


class ThesesSystemSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(models.ThesesSystemSettings, ThesesSystemSettingsAdmin)
