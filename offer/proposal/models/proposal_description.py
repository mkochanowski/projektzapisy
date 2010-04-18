# -*- coding: utf8 -*-

from django.db import models

class ProposalDescription(models.Model):
    proposal = models.ForeignKey('Proposal', related_name = 'descriptions')
    description = models.TextField( verbose_name = 'opis' )
    date = models.DateTimeField(verbose_name = 'data dodania')

    class Meta:
        verbose_name = 'opis przedmiotu'
        verbose_name_plural = 'opisy przedmiotu'
        app_label = 'proposal'

    def __str__(self):
        return self.description

    def __unicode__(self):
        return self.description