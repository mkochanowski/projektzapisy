# -*- coding: utf-8 -*-

from django.contrib import admin

from fereol.offer.proposal.models import *

class ProposalAdmin( admin.ModelAdmin ):
    
    prepopulated_fields = { 'slug' : ( 'name', ) }

        
admin.site.register( Proposal, ProposalAdmin )
admin.site.register( ProposalDescription )
