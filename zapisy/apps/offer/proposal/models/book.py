# -*- coding: utf-8 -*-

"""
    Book for bibliography
"""

from django.db import models

class Book( models.Model ):
    """
        Book for bibliography
    """
    
    proposal_description = models.ForeignKey('ProposalDescription',
                                             verbose_name = 'przedmiot',
                                             related_name = 'books')
    name                 = models.CharField( max_length=255, verbose_name = u'tytuł' )
    order                = models.IntegerField(verbose_name = 'kolejność')
    
    class Meta:
        verbose_name        = 'książka'
        verbose_name_plural = 'książki'
        app_label           = 'proposal'
        ordering            = ('order',)


    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name
