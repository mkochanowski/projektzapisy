# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models

from users.models import Student

from enrollment.subjects.models import *
from exceptions import NonStudentException, NonGroupException, AlreadyAssignedException, OutOfLimitException, AlreadyNotAssignedException
from enrollment.subjects.exceptions import NonSubjectException

from itertools import cycle

COLOR = [
     ('#086808', '#719a71'), #green 
     ('#093a9d', '#5f7ab1'), #blue  
     ('#724848', '#837878'), #brown
     ('#7b267a', '#9b789b'), #violet 
     ('#1B887A', '#7fa6a2'), #ocean 
     ('#AB8B00', '#bdaf70'), #yellow  
     ('#b32727', '#b57272'), #red  
     ('#b10ea7', '#c395c0'), #pink   
]

class Record( models.Model ):
    group = models.ForeignKey(Group, verbose_name = 'grupa')
    student = models.ForeignKey(Student, verbose_name = 'student')

    @staticmethod
    def number_of_students(group):
      """Returns number of students enrolled to particular group"""
      group_ = group
      return Record.objects.filter(group = group_).count()

    @staticmethod
    def get_student_groups(user_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            records = Record.objects.filter(student = student).order_by('group__subject')
            groups = [record.group for record in records]
            subjects = set([group.subject for group in groups])
            subject_color = dict(zip(subjects, cycle(COLOR)))
            for group in groups:
                group.terms_ = group.get_all_terms()
                group.background_color = subject_color[group.subject][1]
                group.border_color = subject_color[group.subject][0]
                group.subject_ = group.subject
            return groups
        except Student.DoesNotExist:
            raise NonStudentException()
    
    @staticmethod
    def get_groups_with_records_for_subject(slug, user_id, group_type):
        try:
            subject = Subject.objects.get(slug=slug)
            groups = Group.objects.filter(subject=subject).filter(type=group_type)
            student_groups = Record.get_groups_for_student(user_id)
            for g in groups:
                g.limit = g.get_group_limit()
                g.classrooms = g.get_all_terms()
                g.enrolled = Record.number_of_students(g)
                if g in student_groups:
                    g.signed = True
        except Subject.DoesNotExist:
            raise NonSubjectException()
        return groups
    
    @staticmethod
    def get_students_in_group(group_id):
        try:
            group = Group.objects.get(id=group_id)
            return map(lambda x: x.student, Record.objects.filter(group=group))
        except Group.DoesNotExist:
            raise NonGroupException()
    
    @staticmethod
    def get_groups_for_student(user_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            return map(lambda x: x.group, Record.objects.filter(student=student))
        except Student.DoesNotExist:
            raise NonStudentException()
    
    @staticmethod
    def is_student_in_subject_group_type(user_id, slug, group_type):
        try:
            student = User.objects.get(id=user_id).student
            subject = Subject.objects.get(slug=slug)
            user_subject_group_type = [g.id for g in Record.get_groups_for_student(user_id) if g.subject == subject and g.type == group_type]
            if user_subject_group_type:
                return user_subject_group_type[0]
            return False
        except Student.DoesNotExist:
            raise NonStudentException()
        except Subject.DoesNotExist:
            raise NonSubjectException()

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
    def change_student_group(user_id, old_id, new_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student  
            old_group = Group.objects.get(id=old_id)
            new_group = Group.objects.get(id=new_id)
            record = Record.objects.get(group=old_group, student=student)
            record.delete()
            Record.objects.create(group=new_group, student=student)
            return record
        except Student.DoesNotExist:
            raise NonStudentException()
        except Group.DoesNotExist:
            raise NonGroupException()
        except Record.DoesNotExist:
            raise AlreadyNotAssignedException()
        
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
        unique_together = (('student', 'group'),)

    def __unicode__(self):
        return "%s (%s - %s)" % (self.group.subject, self.group.get_type_display(), self.group.get_teacher_full_name())
