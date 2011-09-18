# -*- coding: utf-8 -*-

from django.contrib import admin
from apps.enrollment.records.models import *


class RecordAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','student','status','get_semester_name')
    search_fields = ('student__matricula','student__user__first_name','student__user__last_name','group__course__name','group__course__semester__year','group__course__semester__type')
    list_filter = ('status',)

class QueueAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','student','priority')
    search_fields = ('student__matricula','student__user__first_name','student__user__last_name','group__course__name')

admin.site.register( Record, RecordAdmin )
admin.site.register( Queue, QueueAdmin )
