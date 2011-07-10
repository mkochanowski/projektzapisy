# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.users.models import Employee, Student, Program, StudiaZamawiane

class StudentAdmin(admin.ModelAdmin):
    list_display = ('matricula','get_full_name','ects','get_type_of_studies')
    fieldsets = [
        (None,               {'fields': ['user','matricula','status']}),
        ('Studia', {'fields': ['program','semestr']}),
        ('Zapisy', {'fields': ['records_opening_delay_minutes','block']}),
        ('Ogłoszenia mailowe', {'fields': ['receive_mass_mail_enrollment','receive_mass_mail_offer'], 'classes': ['collapse']}),
    ]
    search_fields = ('user__first_name', 'user__last_name', 'matricula')
    list_filter = ('program',)
    ordering = ['user__last_name','user__first_name']
    list_display_links = ('get_full_name',)


class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('get_full_name','homepage','room','consultations',)
    search_fields = ('user__first_name', 'user__last_name', 'user__username')
    fieldsets = [
        (None,               {'fields': ['user','homepage','room','consultations']}),
        ('Ogłoszenia mailowe', {'fields': ['receive_mass_mail_enrollment','receive_mass_mail_offer'], 'classes': ['collapse']}),
    ]
    ordering = ['user__last_name','user__first_name']
    list_display_links = ('get_full_name',)

class StudiaZamawianeAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','points','comments')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__user__matricula')
    ordering = ['student__user__last_name','student__user__first_name']

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Program)
admin.site.register(StudiaZamawiane, StudiaZamawianeAdmin)
