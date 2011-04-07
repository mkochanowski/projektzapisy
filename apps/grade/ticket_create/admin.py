# -*- coding: utf-8 -*-
from django.contrib                    import admin
from apps.grade.ticket_create.models import PublicKey, \
                                              PrivateKey, \
                                              UsedTicketStamp
 
admin.site.register( PublicKey )
admin.site.register( PrivateKey )
admin.site.register( UsedTicketStamp )                                              
                                
