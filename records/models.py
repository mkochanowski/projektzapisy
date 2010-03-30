# -*- coding: utf-8 -*-

from django.db import models
from fereol.users.models import Student
from fereol.subjects.models import *

class Record( models.Model ):
    group = models.ForeignKey(Group, verbose_name = 'grupa')
    student = models.ForeignKey(Student, verbose_name = 'student')
    
    @staticmethod
    def number_of_students(group):
      """Returns number of students enrolled to particular group"""
      group_ = group
      return Record.objects.filter(group = group_).count()

    class Meta:
        verbose_name = 'zapis'
        verbose_name_plural = 'zapisy'
        unique_together = ( ( 'student', 'group' ) , )
    
    def __unicode__(self): 
        return unicode( self.group.subject ) + ' ( ' + PrettyLabel.encode_list( self.group.type, GROUP_TYPE_CHOICES) + ' -  ' + self.group.get_teacher_full_name()  + ' ) '
