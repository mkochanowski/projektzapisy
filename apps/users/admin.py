# -*- coding: utf-8 -*-

from django.contrib import admin

from apps.users.models import Employee, Student, Type

admin.site.register(Employee)
admin.site.register(Student)
admin.site.register(Type)
