# -*- coding: utf-8 -*-

from django.contrib import admin
from django import forms
from django.contrib.auth.models import User

from apps.users.models import Employee, Student, Program, StudiaZamawiane, StudiaZamawianeMaileOpiekunow, ExtendedUser, UserProfile

class ExtendedUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'is_staff')
    fieldsets = [
        (None, {'fields': ('username', 'password')}),
        ('Dane osobowe', {'fields': ('first_name', 'last_name', 'email')}),
        ('Dodatkowe dane', {'fields': ('is_student', 'is_employee', 'is_zamawiany')}),
        ('Uprawnienia', {'fields': ('is_staff', 'is_active', 'is_superuser', 'user_permissions')}),
        ('Ważne daty', {'fields': ('last_login', 'date_joined')}),
        ('Grupy', {'fields': ('groups',)})
    ]
    list_filter = ('is_staff', 'is_superuser', 'is_student', 'is_employee', 'is_zamawiany')
    search_fields = ('username', 'first_name', 'last_name', 'email')

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

    def queryset(self, request):
       qs = super(StudentAdmin, self).queryset(request)
       return qs.select_related('program', 'program__type_of_points', 'user')

class ProgramAdmin(admin.ModelAdmin):

    def queryset(self, request):
       qs = super(ProgramAdmin, self).queryset(request)
       return qs.select_related('type_of_points')
        
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('get_full_name','homepage','room','consultations',)
    list_filter = ('status',)
    search_fields = ('user__first_name', 'user__last_name', 'user__username')
    fieldsets = [
        (None,               {'fields': ['user','status','homepage','room','consultations']}),
        ('Ogłoszenia mailowe', {'fields': ['receive_mass_mail_enrollment','receive_mass_mail_offer'], 'classes': ['collapse']}),
    ]
    ordering = ['user__last_name','user__first_name']
    list_display_links = ('get_full_name',)

    def queryset(self, request):
       qs = super(EmployeeAdmin, self).queryset(request)
       return qs.select_related('user')

class StudentInline(admin.StackedInline):
    model = Student
    extra = 0
    max_num = 1

class EmployeeInline(admin.StackedInline):
    model = Employee
    extra = 0
    max_num = 1

class ProfileInline(admin.StackedInline):
    model = UserProfile

class StudiaZamawianeAdmin(admin.ModelAdmin):
    list_display = ('__unicode__','points','comments')
    search_fields = ('student__user__first_name', 'student__user__last_name', 'student__matricula', 'bank_account')
    ordering = ['student__user__last_name','student__user__first_name']

    def queryset(self, request):
       qs = super(StudiaZamawianeAdmin, self).queryset(request)
       return qs.select_related('student', 'student__user')

from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

UserAdmin.list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff')
UserAdmin.inlines += [ProfileInline, StudentInline, EmployeeInline]
UserAdmin.list_filter = ('is_active', 'is_staff', '_profile_cache__is_student',
                         '_profile_cache__is_employee', '_profile_cache__is_zamawiany')

admin.site.unregister(User)
admin.site.register(User, UserAdmin)


#admin.site.register(ExtendedUser, ExtendedUserAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Program, ProgramAdmin)
admin.site.register(StudiaZamawiane, StudiaZamawianeAdmin)
admin.site.register(StudiaZamawianeMaileOpiekunow)