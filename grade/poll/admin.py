# -*- coding: utf-8 -*-

"""
    Django admin panel for polls
"""

from django.contrib import admin

from grade.poll.models import Poll
from grade.poll.models import Section
from grade.poll.models import Question
from grade.poll.models import Option
from grade.poll.models import GeneratedPoll
                              
admin.site.register( Option )
admin.site.register( Question )
admin.site.register( Section )
admin.site.register( Poll )
admin.site.register( GeneratedPoll )
