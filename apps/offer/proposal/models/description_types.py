# -*- coding: utf-8 -*-

"""
    Types od description
"""

from django.db                            import models
from apps.users.models                         import Program
from apps.enrollment.courses.models          import Type


class DescriptionTypes( models.Model ):
    """
        Types of description
    """
    description         = models.ForeignKey('ProposalDescription',   related_name = 'descriptiontypes')
    lecture_type        = models.ForeignKey('courses.Type',      related_name = 'descriptionstypes')
                
    class Meta:
        verbose_name = 'Typ propozycji'
	verbose_name_plural ='Typy propozycji'
        app_label = 'proposal'
        
    def __unicode__(self):
        return self.lecture_type.__unicode__() + " | " + self.description.__unicode__()
