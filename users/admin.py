# -*- coding: utf-8 -*-

from django.contrib import admin

from fereol.users.models import Employee, Student

admin.site.register(Employee)
admin.site.register(Student)