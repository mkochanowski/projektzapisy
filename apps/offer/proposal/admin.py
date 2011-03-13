# -*- coding: utf-8 -*-

"""
    Proposal administration
"""

from django.contrib import admin

from apps.offer.proposal.models import Proposal, \
                                  ProposalDescription, \
                                  ProposalTag, \
                                  ProposalDescriptionTag,\
                                  Types, \
                                  DescriptionTypes

class ProposalAdmin( admin.ModelAdmin ):
    """
        Proposal administration
    """
    prepopulated_fields = { 'slug' : ( 'name', ) }

        
admin.site.register( Proposal, ProposalAdmin )
admin.site.register( ProposalDescription )
admin.site.register( ProposalTag )
admin.site.register( ProposalDescriptionTag )
admin.site.register( Types )
admin.site.register( DescriptionTypes )
