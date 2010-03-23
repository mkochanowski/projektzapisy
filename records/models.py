# -*- coding: utf-8 -*-

from django.db import models
from fereol.users.models import User
from fereol.subjects.models import Group

class Record( models.Model ):
    group = models.ForeignKey(Group, verbose_name = 'grupa')
    student = models.ForeignKey(User, verbose_name = 'student')

    class Meta:
        verbose_name = 'zapis'
        verbose_name_plural = 'zapisy'
        unique_together = ( ( 'student', 'group' ) , )
    
    def __str__(self):
        return str(self.group.subject) + '(typ:' + str(self.group.type) + ')' # pawel musi naprawic funkcje group_type() zeby dzialala nie tylko dla unicodu
    def __unicode__(self): 
        return unicode(self.group)

