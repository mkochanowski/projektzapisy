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
    list_display = ( 'name', 'owner', )
    search_fields = ( 'name', 'fans', 'teachers', 'tags', 'owner', )
    
class ProposalDescriptionAdmin( admin.ModelAdmin ):
    search_fields = ( 'description', 'requirements', 'comments', 'author', 'tags', )
    list_display = ( 'proposal', 'author', 'date', )
    list_filter= ( 'author', 'tags', )
    list_select_related = True
    
class DescriptionTypesAdmin( admin.ModelAdmin ):
     list_filters = ( 'lecture_type.name', )
        
admin.site.register( Proposal, ProposalAdmin )
admin.site.register( ProposalDescription, ProposalDescriptionAdmin )
admin.site.register( ProposalTag )
admin.site.register( ProposalDescriptionTag )
admin.site.register( Types )
admin.site.register( DescriptionTypes, DescriptionTypesAdmin )
