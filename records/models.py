# -*- coding: utf-8 -*-

from django.db import models
from users.models import Student
from subjects.models import *
from exceptions import NonStudentException, NonGroupException, AlreadyAssignedException, OutOfLimitException, AlreadyNotAssignedException

class Record( models.Model ):
    group = models.ForeignKey(Group, verbose_name = 'grupa')
    student = models.ForeignKey(Student, verbose_name = 'student')

    @staticmethod
    def number_of_students(group):
      """Returns number of students enrolled to particular group"""
      group_ = group
      return Record.objects.filter(group = group_).count()

    @staticmethod
    def add_student_to_group(user_id, group_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            if Record.number_of_students(group=group) < group.limit:
                record, is_created = Record.objects.get_or_create(group=group, student=student)
                if is_created == False:
                    raise AlreadyAssignedException()
            else:
                raise OutOfLimitException()
            return record
        except Student.DoesNotExist:
            raise NonStudentException()
        except Group.DoesNotExist:
            raise NonGroupException()

    @staticmethod
    def remove_student_from_group(user_id, group_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            record = Record.objects.get(group=group, student=student)
            record.delete()
            return record
        except Record.DoesNotExist:
            raise AlreadyNotAssignedException()
        except Student.DoesNotExist:
            raise NonStudentException()
        except Group.DoesNotExist:
            raise NonGroupException()

    def group_slug(self):
        return self.group.subject_slug()

    class Meta:
        verbose_name = 'zapis'
        verbose_name_plural = 'zapisy'
        unique_together = (( 'student', 'group' ),)

    def __unicode__(self):
        return "%s (%s - %s)" % (self.group.subject, self.group.get_type_display(), self.group.get_teacher_full_name())
