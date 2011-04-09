# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.enrollment.subjects.models import *

class SubjectAdmin(admin.ModelAdmin):  
    prepopulated_fields = {'slug' : ('name', 'semester')}
    list_display = ('name', 'semester', 'lectures', 'exercises', 'laboratories','repetitions')
    list_filter = ('semester',)
    search_fields = ('name',)
    fieldsets = [
        (None,               {'fields': ['entity','name']}),
        ('Szczegóły', {'fields': ['teachers','description','semester','type','slug'], 'classes': ['collapse']}),
        ('Wymiar godzinowy zajęć', {'fields': ['lectures','exercises','laboratories','repetitions'], 'classes': ['collapse']}),
    ]

class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('number', 'capacity', 'building')
    list_filter = ('building','capacity')

class SemesterAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'visible')
    list_filter = ('visible','year','type')
    fieldsets = [
        (None,               {'fields': ['year','type','visible']}),
        ('Czas trwania semestru', {'fields': ['semester_beginning','semester_ending']}),
        ('Czas trwania zapisów', {'fields': ['records_opening','records_closing']}),
    ]

class SubjectInline(admin.TabularInline):
    model = Subject

class SubjectEntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'shortName')
    search_fields = ('name', 'shortName')
    inlines = [
        SubjectInline,
    ]
        
class PointsOfSubjectsAdmin(admin.ModelAdmin):
    list_display = ('subject', 'program', 'value')
    search_fields = ('subject__name', )
    list_filter = ('program',)

class GroupAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    search_fields = ('subject','teacher')

class TypeAdmin(admin.ModelAdmin):
    list_display = ('name','group','meta_type')
    list_filter = ('group','meta_type')

class TermAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['group']}),
        ('Termin', {'fields': ['dayOfWeek','start_time','end_time']}),
        ('Miejsce', {'fields': ['classroom']}),
    ]
    list_filter = ('classroom','dayOfWeek')
    list_display = ('__unicode__','group')

class StudentOptionsAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','records_opening_delay_minutes')
    search_fields = ('student__matricula','student__user__first_name','student__user__last_name','subject__name')

admin.site.register(Subject, SubjectAdmin)
admin.site.register(SubjectEntity, SubjectEntityAdmin)
admin.site.register(StudentOptions,StudentOptionsAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Classroom, ClassroomAdmin)
admin.site.register(Term, TermAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(PointTypes)
admin.site.register(PointsOfSubjects, PointsOfSubjectsAdmin)
admin.site.register(PointsOfSubjectEntities)
