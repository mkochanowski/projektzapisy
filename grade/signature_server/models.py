# -*- coding: utf-8 -*-
from django.db                  import models
from grade.cryptography.models  import GroupsConnection
from users.models               import Student
from enrollment.subjects.models import Semester

class UsedTicketStamp( models.Model ):
    student           = models.ForeignKey( Student,
                                           verbose_name = "student" )
    groups_connection = models.ForeignKey( GroupsConnection,
                                           verbose_name = "powiązanie grup" )
    # semester          = models.ForeignKey( Semester,
    #                                        verbose_name = "semestr" ) do dodania niebawem

    def __unicode__(self):
        return unicode(self.student)+ " " + unicode(self.groups_connection) # + " " + unicode(self.semester)
