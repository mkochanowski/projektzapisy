# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.enrollment.courses.models import *
from apps.enrollment.records.models import Record

class GroupInline(admin.TabularInline):
    model = Group
    extra = 0
    raw_id_fields = ("teacher",)

class CourseAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug' : ('name', 'semester')}
    list_display = ('name', 'semester', 'lectures', 'exercises_laboratories','exercises', 'laboratories','repetitions')
    list_filter = ('semester','type')
    search_fields = ('name',)
    fieldsets = [
        (None,               {'fields': ['entity','name'], 'classes': ['long_name']}),
        ('Szczegóły', {'fields': ['teachers','requirements','description','semester','english','exam','suggested_for_first_year','type','slug','web_page'], 'classes': ['collapse']}),
        ('Wymiar godzinowy zajęć', {'fields': ['lectures','exercises_laboratories','exercises','laboratories','repetitions'], 'classes': ['collapse']}),
    ]
    inlines = [GroupInline, ]
    filter_horizontal = ['requirements']

    def queryset(self, request):
       """
       Filter the objects displayed in the change_list to only
       display those for the currently signed in user.
       """
       qs = super(CourseAdmin, self).queryset(request)
       return qs.select_related('semester', 'type')

class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('number', 'capacity', 'building')
    list_filter = ('building','capacity')

class SemesterAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'visible')
    list_filter = ('visible','year','type')
    fieldsets = [
        (None,               {'fields': ['year','type','visible']}),
        ('Czas trwania semestru', {'fields': ['semester_beginning','semester_ending']}),
        ('Czas trwania zapisów', {'fields': ['records_opening','records_ects_limit_abolition','records_closing']}),
    ]
    list_editable = ('visible',)

class CourseInline(admin.TabularInline):
    model = Course

class CourseEntityAdmin(admin.ModelAdmin):
    list_display = ('name', 'shortName')
    search_fields = ('name', 'shortName')
    fieldsets = [
        (None,               {'fields': ['name','shortName','type','description'], 'classes': ['long_name']}),
        ('Wymiar godzinowy zajęć', {'fields': ['lectures','exercises','laboratories','repetitions'], 'classes': ['collapse']}),
    ]
        
class PointsOfCoursesAdmin(admin.ModelAdmin):
    list_display = ('course', 'program','type_of_point','value')
    search_fields = ('course__name', )
    list_filter = ('program',)

class TermInline(admin.TabularInline):
    model = Term
    extra = 0

class RecordInline(admin.TabularInline):
    model = Record
    extra = 0
    raw_id_fields = ("student",)

class GroupAdmin(admin.ModelAdmin):
    list_display = ('course', 'teacher','type','limit','limit_zamawiane','get_terms_as_string')
    list_filter = ('type','teacher',)
    search_fields = ('teacher__user__first_name','teacher__user__last_name','course__name')
    inlines = [
        TermInline,RecordInline
    ]
    def queryset(self, request):
       """
       Filter the objects displayed in the change_list to only
       display those for the currently signed in user.
       """
       qs = super(GroupAdmin, self).queryset(request)
       return qs.select_related('teacher', 'teacher__user', 'course', 'course__semester', 'course__type')

class TypeAdmin(admin.ModelAdmin):
    list_display = ('name','group','meta_type')
    list_filter = ('group','meta_type')


class TermAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,               {'fields': ['group']}),
        ('Termin', {'fields': ['dayOfWeek','start_time','end_time']}),
        ('Miejsce', {'fields': ['classrooms',]}),
    ]
    list_filter = ('dayOfWeek',)
    list_display = ('__unicode__','group')
    search_fields = ('group__course__name','group__teacher__user__first_name','group__teacher__user__last_name','dayOfWeek')
    def queryset(self, request):
       """
       Filter the objects displayed in the change_list to only
       display those for the currently signed in user.
       """
       qs = super(TermAdmin, self).queryset(request)
       return qs.select_related('classrooms', 'group')

class StudentOptionsAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','records_opening_bonus_minutes')
    search_fields = ('student__matricula','student__user__first_name','student__user__last_name','course__name')

admin.site.register(Course, CourseAdmin)
admin.site.register(CourseEntity, CourseEntityAdmin)
admin.site.register(StudentOptions,StudentOptionsAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Classroom, ClassroomAdmin)
admin.site.register(Term, TermAdmin)
admin.site.register(Semester, SemesterAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(PointTypes)
admin.site.register(PointsOfCourses, PointsOfCoursesAdmin)
admin.site.register(PointsOfCourseEntities)
