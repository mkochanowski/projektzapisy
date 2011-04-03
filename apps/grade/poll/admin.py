# -*- coding: utf-8 -*-

"""
    Django admin panel for polls
"""

from django.contrib import admin
from django.db import models

from apps.grade.poll.models import Answer
from apps.grade.poll.models import OpenQuestion
from apps.grade.poll.models import SingleChoiceQuestion
from apps.grade.poll.models import MultipleChoiceQuestion
from apps.grade.poll.models import Poll

class AnswerAdmin(admin.ModelAdmin):
    search_fields = ( 'contents', )
    
class OpenQuestionAdmin(admin.ModelAdmin):
    search_fields = ( 'contents', )
       
class SingleChoiceQuestionAdmin(admin.ModelAdmin):
    search_fields = ( 'contents', )
    
class MultipleChoiceQuestionAdmin(admin.ModelAdmin):
    search_fields = ( 'contents', )
    
class PollAdmin(admin.ModelAdmin):
    search_fields = ( 'title', 'author', 'subject', 'group' )
    list_display = ( 'group', 'subject', 'author', )
                              
admin.site.register( Answer, AnswerAdmin )
admin.site.register( OpenQuestion, OpenQuestionAdmin )
admin.site.register( SingleChoiceQuestion, SingleChoiceQuestionAdmin )
admin.site.register( MultipleChoiceQuestion, MultipleChoiceQuestionAdmin )
admin.site.register( Poll, PollAdmin )
