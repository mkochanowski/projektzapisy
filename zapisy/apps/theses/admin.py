from django.contrib import admin

from . import models, forms


class ThesisAdmin(admin.ModelAdmin):
    """A custom form for thesis objects, see forms.py for an explanation"""
    form = forms.ThesisForm


admin.site.register(models.Thesis, ThesisAdmin)
