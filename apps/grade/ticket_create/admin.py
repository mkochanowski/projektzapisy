# -*- coding: utf-8 -*-
from django.contrib                    import admin
from apps.grade.ticket_create.models import PublicKey, \
                                              PrivateKey, \
                                              UsedTicketStamp, StudentGraded


class StudentGradedAdmin( admin.ModelAdmin ):
    list_display = ('student', 'student__matricula', 'semester')
    search_fields = ('student__matricula','student__user__first_name','student__user__last_name','semester')

admin.site.register( PublicKey )
admin.site.register( PrivateKey )
admin.site.register( UsedTicketStamp )                                              
admin.site.register( StudentGraded, StudentGradedAdmin )

