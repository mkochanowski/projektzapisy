# -*- coding: utf-8 -*-

from django.db import models
from fereol.users.models import User
from fereol.subjects.models import Group, group_type

class Record( models.Model ):
    group = models.ForeignKey(Group, verbose_name = 'grupa')
    student = models.ForeignKey(User, verbose_name = 'student')

    class Meta:
        verbose_name = 'zapis'
        verbose_name_plural = 'zapisy'
        unique_together = ( ( 'student', 'group' ) , )
    
    def __unicode__(self): 
        return unicode( self.group.subject ) + ' ( ' + group_type( self.group.type ) + ' -  ' + self.group.get_teacher_full_name()  + ' ) '

