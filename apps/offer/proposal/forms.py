# -*- coding: utf-8 -*-
from django.forms.models import ModelForm, inlineformset_factory, modelformset_factory
from django.shortcuts import get_object_or_404
from apps.enrollment.courses.models.course import CourseEntity
from apps.offer.proposal.models.book import Book
from apps.offer.proposal.models.proposal import Proposal
from apps.offer.proposal.models.proposal_description import ProposalDescription


class ProposalForm(ModelForm):

    class Meta:
        exclude=('slug', 'owner', 'hidden', 'deleted', 'student')
        model = CourseEntity

