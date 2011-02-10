# -*- coding: utf-8 -*-

from django.contrib import admin

from fereol.users.models import Employee, Student, Type, Program

class StudentAdmin(admin.ModelAdmin):
    list_display = ('matricula','ects','program')
    search_fields = ('user__first_name', 'user__last_name', 'matricula')
    list_filter = ('program',)

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user','consultations',)
    search_fields = ('user__first_name', 'user__last_name', 'user__username')

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Program)
