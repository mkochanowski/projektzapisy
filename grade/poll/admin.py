# -*- coding: utf-8 -*-

"""
    Django admin panel for polls
"""

from django.contrib import admin

from grade.poll.models import Answer
from grade.poll.models import OpenQuestion
from grade.poll.models import SingleChoiceQustion
from grade.poll.models import MultipleChoiceQuestion
from grade.poll.models import Poll
                              
admin.site.register( Answer )
admin.site.register( OpenQuestion )
admin.site.register( SingleChoiceQustion )
admin.site.register( MultipleChoiceQuestion )
admin.site.register( Poll )
