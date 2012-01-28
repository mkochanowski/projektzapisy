# -*- coding: utf-8 -*-
from django.contrib                    import admin
from apps.grade.ticket_create.models import PublicKey, \
                                              PrivateKey, \
                                              UsedTicketStamp, StudentGraded


class StudentGradedAdmin( admin.ModelAdmin ):
    list_display = ('student',  'semester')
    search_fields = ('student',)

admin.site.register( PublicKey )
admin.site.register( PrivateKey )
admin.site.register( UsedTicketStamp )                                              
admin.site.register( StudentGraded, StudentGradedAdmin )

