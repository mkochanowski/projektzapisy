# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms
from django.contrib.auth.models import User

from apps.users.models import Employee, Student, Program, StudiaZamawiane, StudiaZamawianeMaileOpiekunow

class StudentAdmin(admin.ModelAdmin):
    list_display = ('matricula','get_full_name','ects','get_type_of_studies')
    fieldsets = [
        (None,               {'fields': ['user','matricula','status']}),
        ('Studia', {'fields': ['program','semestr','ects']}),
        ('Zapisy', {'fields': ['records_opening_bonus_minutes','block']}),
        ('Inne', {'fields': ['receive_mass_mail_enrollment','receive_mass_mail_offer','receive_mass_mail_grade','last_news_view'], 'classes': ['collapse']}),
    ]
    search_fields = ('user__first_name', 'user__last_name', 'matricula')
    list_filter = ('program','status','semestr')
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
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__matricula', 'bank_account')
    ordering = ['student__user__last_name','student__user__first_name']

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Program)
admin.site.register(StudiaZamawiane, StudiaZamawianeAdmin)
admin.site.register(StudiaZamawianeMaileOpiekunow)