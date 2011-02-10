# -*- coding: utf-8 -*-

from django.contrib import admin

from fereol.enrollment.subjects.models import *

class SubjectAdmin(admin.ModelAdmin):  
    prepopulated_fields = {'slug' : ('name',)}

class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('number', 'capacity', 'building')

class SemesterAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'visible')

class SubjectEntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'shortName')
    search_fields = ('name', 'shortName')
        
admin.site.register(Subject, SubjectAdmin)
admin.site.register(SubjectEntity, SubjectEntityAdmin)
admin.site.register(StudentOptions)
admin.site.register(Group)
admin.site.register(Classroom, ClassroomAdmin)
admin.site.register(Term)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Type)

