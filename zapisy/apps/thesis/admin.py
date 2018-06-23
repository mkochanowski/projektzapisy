from django.contrib import admin

from . import models

admin.site.register(models.Thesis)
admin.site.register(models.ThesisCommissionMember)
admin.site.register(models.ThesisVoteBinding)
admin.site.register(models.ThesisSystemSettings)
