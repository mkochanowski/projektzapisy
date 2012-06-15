# -*- coding: utf-8 -*-

"""
    Form for vote
"""

from django                   import forms
from django.core.exceptions   import ObjectDoesNotExist
from django.utils.safestring  import SafeUnicode
from apps.enrollment.courses.models.course import CourseEntity

from apps.offer.vote.models import SystemState
from apps.offer.vote.models import SingleVote
from django.core.urlresolvers import reverse

import settings

class VoteFormset():
    """
        Class
    """
    def __init__(self, post, *args, **kwargs):
        from django.forms.models import modelformset_factory

        tag             = kwargs.pop('tag',        None)
        student         = kwargs.pop('student',    None)
        self.correction = kwargs.pop('correction', None)

        if tag == 'winter':
            proposals  = CourseEntity.objects.filter(status=2, semester='z', deleted=False)
        elif tag == 'summer':
            proposals  = CourseEntity.objects.filter(status=2, semester='l', deleted=False)
        else:
            tag = 'unknown'
            proposals = CourseEntity.objects.filter(status=2, semester='u', deleted=False)

        votes = SingleVote.get_votes_for_proposal(student, proposals)


        fields = ('correction',) if self.correction else ('value',)


        SingleVoteFormset = modelformset_factory( SingleVote,
                                                  fields = fields,
                                                  extra  = 0 )

        self.formset = SingleVoteFormset(post,
                                         queryset = votes,
                                         prefix   = tag )
        self.errors  = []

    def points(self):
        counter = 0

        field = 'correction' if self.correction else 'value'

        for form in self.formset:
            if not form.instance.entity.type.free_in_vote:
                counter += form.cleaned_data[field]

        return counter

    def is_valid(self):
        if self.formset.is_valid():

            if self.correction:
                for form in self.formset:
                    if form.instance.value > form.cleaned_data['correction']:
                        self.errors.append( u'Nie można zmniejszyć głosu!' )
                        return False

            return True

        return False


    def save(self):

        instances = self.formset.save(commit=False)

        if not self.correction:
            for instance in instances:
                instance.correction = instance.value
                instance.save()

        return instances


class VoteFormsets():

    def __init__(self, post=None, student=None, state=None, *args, **kwargs):

        if state.is_correction_active():
            correction        = True
            votes             = SingleVote.sum_votes(student, state)
            self.points_limit = votes['votes']

        else:
            correction        = False
            self.points_limit = state.max_points

        self.summer  = VoteFormset(post,
                                   student    = student,
                                   tag        = 'summer',
                                   correction = correction)
        self.winter  = VoteFormset(post,
                                   student    = student,
                                   tag        = 'winter',
                                   correction = correction)
        self.unknown = VoteFormset(post,
                                   student    = student,
                                   correction = correction)
        self.errors = []


    def points(self):
        return self.summer.points() +\
               self.winter.points() +\
               self.unknown.points()
    
    def is_valid(self):

        self.errors = self.errors + self.summer.errors
        self.errors = self.errors + self.winter.errors
        self.errors = self.errors + self.unknown.errors

        is_valid = self.summer.is_valid() and self.winter.is_valid() and self.unknown.is_valid()

        if not is_valid:
                return False


        points = self.points()
        if  points > self.points_limit:
            self.errors.append(u'Limit ' + str(self.points_limit) +u' punktów przekroczony o ' + \
                               str((points - self.points_limit)) )
            return False


        return True


    def save(self):
        self.summer.save()
        self.winter.save()
        self.unknown.save()

