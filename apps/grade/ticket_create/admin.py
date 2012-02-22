# -*- coding: utf-8 -*-
from django.contrib                    import admin
from apps.grade.ticket_create.models import PublicKey, \
                                              PrivateKey, \
                                              UsedTicketStamp, StudentGraded


class StudentGradedAdmin( admin.ModelAdmin ):
    list_display = ('student',  'semester')
    search_fields = ('student__user__first_name',
                     'student__user__last_name',
                     'student__matricula',)

class UsedTicketStampAdmin( admin.ModelAdmin ):
    list_display = ['student', 'poll' ]
    search_fields = ('student__user__first_name',
                     'student__user__last_name',
                     'student__matricula',)

admin.site.register( PublicKey )
admin.site.register( PrivateKey )
admin.site.register( UsedTicketStamp, UsedTicketStampAdmin )
admin.site.register( StudentGraded, StudentGradedAdmin )

