# -*- coding: utf-8 -*-

from django.contrib import admin

from fereol.subjects.models import *

class SubjectAdmin( admin.ModelAdmin ):
    
    prepopulated_fields = { 'slug' : ( 'name', ) }

        
admin.site.register( Subject, SubjectAdmin )
admin.site.register( SubjectDescription)
admin.site.register( Group )