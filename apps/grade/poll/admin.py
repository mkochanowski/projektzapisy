# -*- coding: utf-8 -*-

"""
    Django admin panel for polls
"""

from django.contrib import admin

from apps.grade.poll.models import Answer
from apps.grade.poll.models import OpenQuestion
from apps.grade.poll.models import SingleChoiceQuestion
from apps.grade.poll.models import MultipleChoiceQuestion
from apps.grade.poll.models import Poll
                              
admin.site.register( Answer )
admin.site.register( OpenQuestion )
admin.site.register( SingleChoiceQuestion )
admin.site.register( MultipleChoiceQuestion )
admin.site.register( Poll )
