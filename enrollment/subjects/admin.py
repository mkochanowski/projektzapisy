# -*- coding: utf-8 -*-

from django.contrib import admin

from fereol.enrollment.subjects.models import *

class SubjectAdmin(admin.ModelAdmin):
    
    prepopulated_fields = {'slug' : ('name',)}

        
admin.site.register(Subject, SubjectAdmin)
admin.site.register(SubjectEntity)
admin.site.register(Group)
admin.site.register(Classroom)
admin.site.register(Term)
admin.site.register(Semester)
admin.site.register(Type)

