# -*- coding: utf-8 -*-

"""
    Description of proposal
"""
from django.core.exceptions import ObjectDoesNotExist

from django.db import models
from django.contrib.auth.models import User


class NoRemovedManager(models.Manager):
    def get_query_set(self):
        return super(NoRemovedManager, self).get_query_set().filter(deleted=False)

class ProposalDescription(models.Model):
    """
        Description of proposal
    """
#    proposal     = models.ForeignKey('Proposal', related_name = 'descriptions_set')
#    description  = models.TextField( verbose_name = 'opis' )
#    requirements = models.TextField( verbose_name = 'wymagania' )
#    comments     = models.TextField( blank = True, null=True,
#                                     verbose_name = 'uwagi' )
#    date         = models.DateTimeField(auto_now=True,
#                                        verbose_name = 'data dodania')
#    author       = models.ForeignKey(User, related_name='autor')
#
#    deleted      = models.BooleanField(default=False,
#                                       verbose_name='usunięty')
#    exam         = models.BooleanField(choices=((False, 'Nie'), (True, 'Tak')),
#                                       default=False,
#                                       verbose_name='z egzaminem')
#    english      = models.BooleanField(default=False,
#                                       verbose_name=u'możliwe zajęcia po angielsku')
#    web_page     = models.URLField( verbose_name = 'Strona WWW przedmiotu',
#                                verify_exists= True,
#								blank        = True,
#                                null         = True )
#    type         = models.ForeignKey('courses.Type',      related_name = 'descriptionstypes')

    objects      = models.Manager()
    noremoved    = NoRemovedManager()

    class Meta:
        verbose_name = 'opis przedmiotu'
        verbose_name_plural = 'opisy przedmiotów'
        app_label = 'proposal'

    def __unicode__(self):
        return '[' + self.author.__unicode__() + ']' + self.proposal.name 

    def get_newer(self):
        try:
            return ProposalDescription.noremoved.filter(proposal=self.proposal, id__gt=self.id).order_by('date')[0:1].get()
        except ObjectDoesNotExist:
            return None

    def get_older(self):
        try:
            return ProposalDescription.noremoved.filter(proposal=self.proposal, date__lt=self.date).order_by('-date')[0:1].get()
        except ObjectDoesNotExist:
            return None
