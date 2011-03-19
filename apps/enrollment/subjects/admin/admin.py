# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.enrollment.subjects.models import *

class SubjectAdmin(admin.ModelAdmin):  
    prepopulated_fields = {'slug' : ('name',)}
    list_display = ('name', 'semester', 'lectures', 'exercises', 'laboratories','repetitions')
    list_filter = ('semester',)
    search_fields = ('name',)

class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('number', 'capacity', 'building')

class SemesterAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'visible')

class SubjectEntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'shortName')
    search_fields = ('name', 'shortName')
        
class PointsOfSubjectsAdmin(admin.ModelAdmin):
    list_display = ('subject', 'program', 'value')
    search_fields = ('subject__name', )
    list_filter = ('program',)

admin.site.register(Subject, SubjectAdmin)
admin.site.register(SubjectEntity, SubjectEntityAdmin)
admin.site.register(StudentOptions)
admin.site.register(Group)
admin.site.register(Classroom, ClassroomAdmin)
admin.site.register(Term)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Type)
admin.site.register(PointTypes)
admin.site.register(PointsOfSubjects, PointsOfSubjectsAdmin)
