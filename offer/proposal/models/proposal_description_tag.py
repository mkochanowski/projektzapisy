# -*- coding: utf-8 -*-

"""
    Tag for proposal description
"""

from django.db import models

class ProposalDescriptionTag(models.Model):
    """
        Tag for proposal description
    """
    name = models.CharField(max_length = 255,
                            verbose_name = 'etykieta',
                            unique = True)
    
    class Meta:
        verbose_name = 'etykieta opisu przedmiotu'
        verbose_name_plural = 'etykiety opisu przedmiotu'
        app_label = 'proposal'
    
    def __unicode__(self):
        return self.name
