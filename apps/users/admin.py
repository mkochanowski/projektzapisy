# -*- coding: utf-8 -*-

from django.contrib import admin

from fereol.users.models import Employee, Student, Program

class StudentAdmin(admin.ModelAdmin):
    list_display = ('matricula','get_full_name','ects','get_type_of_studies')
    search_fields = ('user__first_name', 'user__last_name', 'matricula')
    list_filter = ('program',)

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('user','homepage','room','consultations',)
    search_fields = ('user__first_name', 'user__last_name', 'user__username')

admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Student, StudentAdmin)
admin.site.register(Program)
