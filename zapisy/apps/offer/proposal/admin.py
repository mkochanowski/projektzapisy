# -*- coding: utf-8 -*-

"""
    Proposal administration
"""

from django.contrib import admin

from apps.offer.proposal.models import Proposal, \
                                  ProposalDescription, \
                                  Book
#
#class ProposalAdmin( admin.ModelAdmin ):
#    """
#        Proposal administration
#    """
#    prepopulated_fields = { 'slug' : ( 'name', ) }
#    list_display = ( 'name', 'owner', )
#    search_fields = ( 'name', 'owner', )
#    fieldsets = [
#        (None,               {'fields': ['name','owner', 'slug' ], 'classes': ['long_name']}),
#        (None,          {'fields': [ 'semester', 'status', 'deleted', 'hidden', 'student']}),
#    ]
#
#class BookInline(admin.TabularInline):
#    model = Book
#
#class ProposalDescriptionAdmin( admin.ModelAdmin ):
#    search_fields = ( 'description', 'requirements', 'comments', 'author', )
#    list_display = ( 'proposal', 'author', 'date', )
#    list_filter= ( 'author', )
#    list_select_related = True
#    inlines = [
#        BookInline,
#    ]
#
#
#admin.site.register( Proposal, ProposalAdmin )
#admin.site.register( ProposalDescription, ProposalDescriptionAdmin )
