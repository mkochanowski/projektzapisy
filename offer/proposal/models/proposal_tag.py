# -*- coding: utf-8 -*-

from django.db import models

class ProposalTag(models.Model):
    "Tag for a proposal"
    name = models.CharField(max_length = 255,
                            verbose_name = 'etykieta',
                            unique = True)
    
    class Meta:
        verbose_name = 'etykieta przedmiotu'
        verbose_name_plural = 'etykiety przedmiotu'
        app_label = 'proposal'
    
    def __unicode__(self):
        return self.name
