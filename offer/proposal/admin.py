# -*- coding: utf-8 -*-

"""
    Proposal administration
"""

from django.contrib import admin

from offer.proposal.models import Proposal, \
                                  ProposalDescription, \
                                  ProposalTag, \
                                  ProposalDescriptionTag

class ProposalAdmin( admin.ModelAdmin ):
    """
        Proposal administration
    """
    prepopulated_fields = { 'slug' : ( 'name', ) }

        
admin.site.register( Proposal, ProposalAdmin )
admin.site.register( ProposalDescription )
admin.site.register( ProposalTag )
admin.site.register( ProposalDescriptionTag )
