# -*- coding: utf-8 -*-

"""
    Form for vote
"""

from django                   import forms
from django.core.exceptions   import ObjectDoesNotExist
from django.utils.safestring  import SafeUnicode

from apps.offer.vote.models import SystemState
from apps.offer.vote.models import SingleVote
from django.core.urlresolvers import reverse

import settings

class VoteFormset():
    def __init__(self, post, *args, **kwargs):
        from apps.offer.proposal.models.proposal import Proposal
        from django.forms.models import modelformset_factory
        from django.db.models import Q

        tag             = kwargs.pop('tag',        None)
        student         = kwargs.pop('student',    None)
        self.correction = kwargs.pop('correction', None)

        if not tag:
            tag = 'unknown'
            proposals = Proposal.objects\
                        .filter(Q(tags__name='vote'),\
                               ~Q(tags__name='summer'),
                               ~Q(tags__name='winter'))
            self.votes = SingleVote.get_votes_for_proposal(student, proposals)
        else:
            proposals  = Proposal.get_by_tag(tag)
            self.votes = SingleVote.get_votes_for_proposal(student, proposals)

        if self.correction:
            fields = ('correction',)
        else:
            fields = ('value',)

        SingleVoteFormset = modelformset_factory( SingleVote, fields=fields, extra=0 )


        self.formset = SingleVoteFormset(post, queryset=self.votes, prefix=tag )
        self.errors  = []

    def points(self):
        counter = 0

        if self.correction:
            for form in self.formset:
                counter += max(form.instance.value, form.cleaned_data['correction'])
        else:
            for form in self.formset:
                counter += form.cleaned_data['value']

    def is_valid(self):
        if self.formset.is_valid():

            if self.correction:
                for form in self.formset:
                    if form.instance.value > form.cleaned_data['correction']:
                        self.errors.append( u'Nie można zmniejszyć głosu!' )
                        return False

            return True

        else:
            return False


    def save(self):
        self.formset.save()
        #TODO: How to do it better?
        if not self.correction:
            for form in self.formset:
                vote = form.instance
                vote.correction = vote.value
                vote.save()

        return True


class VoteFormsets():

    def __init__(self, post=None, student=None, state=None, *args, **kwargs):

        if state.is_correction_active():
            correction        = True
            votes             = SingleVote.sum_votes(student, state)
            self.points_limit = votes['votes']

        else:
            correction        = False
            self.points_limit = state.max_points

        self.summer  = VoteFormset(post, student=student, tag='summer',  correction=correction)
        self.winter  = VoteFormset(post, student=student, tag='winter', correction=correction)
        self.unknown = VoteFormset(post, student=student, correction=correction)
        self.errors = []


    def points(self):
        return self.summer.points() +\
               self.winter.points() +\
               self.unknown.points()
    
    def is_valid(self):

        if not self.summer.is_valid():
            self.errors = self.errors + self.summer.errors
            return False

        if not self.winter.is_valid():
            self.errors = self.errors + self.winter.errors
            return False

        if not self.unknown.is_valid():
            self.errors = self.errors + self.unknown.errors
            return False

        points = self.points()

        if points > self.points_limit:
            self.errors.append(u'Limit ' + str(self.points_limit) +u' punktów przekroczony o ' + \
                               str((points - self.points_limit)) )
            return False

        else:
            return True


    def save(self):
        self.summer.save()
        self.winter.save()
        self.unknown.save()

