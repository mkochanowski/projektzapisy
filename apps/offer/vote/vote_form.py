# -*- coding: utf-8 -*-

"""
    Form for vote
"""

from django                   import forms
from django.core.exceptions   import ObjectDoesNotExist
from django.db.models import Sum
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
        state           = kwargs.pop('state',    None)
        self.correction = kwargs.pop('correction', None)

        query = {}
        query['status'] = 2
        query['deleted'] = False

        if tag == 'winter':
            query['semester'] = 'z'
        elif tag == 'summer':
            query['semester'] = 'l'
        else:
            tag = 'unknown'
            query['semester'] = 'u'

        proposals  = CourseEntity.objects.filter(**query)
        votes = SingleVote.get_votes_for_proposal(student, proposals)
        counter = votes.exclude(entity__type__free_in_vote=True).aggregate(Sum('value'))
        self.old_votes = counter['value__sum']

        if self.correction:
            votes = votes.filter(course__isnull=False)


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
            sum_points = 0
            if self.correction:
                for form in self.formset:
                    sum_points += form.cleaned_data['correction']
                    if form.instance.value > form.cleaned_data['correction']:
                        self.errors.append( u'Nie można zmniejszyć głosu!' )
                        return False

                if sum_points > self.old_votes:
                    self.errors.append(u'Przekroczono limit głosów o: ' + str(sum_points - self.old_votes))
                    return False

            return True

        return False


    def save(self):



        if not self.correction:
            instances = self.formset.save(commit=False)
            for instance in instances:
                instance.correction = instance.value
                instance.save()

            return instances

        else:
            return self.formset.save()


class VoteFormsets():

    def __init__(self, post=None, student=None, state=None, *args, **kwargs):
        self.summer = None
        self.winter = None
        self.unknown = None
        if state.is_correction_active():
            correction        = True
            votes             = SingleVote.sum_votes(student, state)
            self.points_limit = 0
            if state.is_summer_correction_active():
                self.summer  = VoteFormset(post,
                                           student    = student,
                                           tag        = 'summer',
                                           correction = correction)

                self.points_limit += self.summer.old_votes

            if state.is_winter_correction_active():
                self.winter  = VoteFormset(post,
                                       student    = student,
                                       tag        = 'winter',
                                       correction = correction)
                self.points_limit += self.winter.old_votes

            self.errors = []

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
        points = 0
        if self.summer:
            points += self.summer.points()
        if self.winter:
            points += self.winter.points()
        if self.unknown:
            points += self.unknown.points()

        return points
    
    def is_valid(self):

        if self.summer:
            self.errors = self.errors + self.summer.errors
        if self.winter:
            self.errors = self.errors + self.winter.errors
        if self.unknown:
            self.errors = self.errors + self.unknown.errors

        is_valid = (not self.summer or self.summer.is_valid()) and\
                   (not self.winter or self.winter.is_valid()) and\
                   (not self.unknown or self.unknown.is_valid())



        if not is_valid:
            return False


        points = self.points()
        if  points > self.points_limit:
            self.errors.append(u'Limit ' + str(self.points_limit) +u' punktów przekroczony o ' + \
                               str((points - self.points_limit)) )
            return False


        return True


    def save(self):
        if self.summer:
            self.summer.save()
        if self.winter:
            self.winter.save()
        if self.unknown:
            self.unknown.save()

