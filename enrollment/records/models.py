# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models

from users.models import Student

from enrollment.subjects.models import *
from enrollment.records.exceptions import *
from enrollment.subjects.exceptions import NonSubjectException, NonStudentOptionsException

from itertools import cycle

STATUS_ENROLLED = '1'
STATUS_PINNED = '2'
RECORD_STATUS = [( STATUS_ENROLLED, u'zapisany' ), ( STATUS_PINNED, u'oczekujący' )]

import logging
logger = logging.getLogger()

class EnrolledManager(models.Manager):
    def get_query_set(self):
        """ Returns only enrolled students. """
        return super(EnrolledManager, self).get_query_set().filter(status = STATUS_ENROLLED)

class Record( models.Model ):
    group = models.ForeignKey(Group, verbose_name = 'grupa')
    student = models.ForeignKey(Student, verbose_name = 'student', related_name='records')
    status = models.CharField(max_length = 1, choices = RECORD_STATUS, verbose_name = 'status')
    
    objects = models.Manager()
    enrolled = EnrolledManager()
    
    @staticmethod
    def number_of_students(group):
        """Returns number of students enrolled to particular group"""
        group_ = group
        return Record.enrolled.filter(group = group_).count()

    @staticmethod
    def get_student_all_detiled_records(user_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            records = Record.objects.filter(student = student).\
                select_related('group', 'group__subject').order_by('group__subject')
            for record in records:
                record.group_ = record.group
                record.group_.terms_ = record.group.get_all_terms()
                record.group_.subject_ = record.group.subject
                if record.status == STATUS_ENROLLED:
                    record.schedule_widget_status_ = 'fixed'
                elif record.status == STATUS_PINNED:
                    record.schedule_widget_status_ = 'pinned'
                else:
                    record.schedule_widget_status_ = ''
            return records
        except Student.DoesNotExist:
            logger.error('Record.get_student_all_detiled_records(user_id = %d) throws Student.DoesNotExist exception.' % user_id )
            raise NonStudentException()
    
    @staticmethod    
    def get_student_all_detiled_enrollings(user_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            records = Record.enrolled.filter(student = student).\
                select_related('group', 'group__subject').order_by('group__subject')
            groups = [record.group for record in records]
            subjects = set([group.subject for group in groups])
            for group in groups:
                group.terms_ = group.get_all_terms()
                group.subject_ = group.subject
            return groups
        except Student.DoesNotExist:
            logger.error('Record.get_student_all_detiled_enrollings(user_id = %d) throws Student.DoesNotExist exception.' % user_id )           
            raise NonStudentException()
         
    @staticmethod
    def get_groups_with_records_for_subject(slug, user_id, group_type):
        try:
            subject = Subject.objects.get(slug=slug)
            groups = Group.objects.filter(subject=subject).filter(type=group_type)
            try:
                student_groups = Record.get_groups_for_student(user_id)
            except NonStudentException:
                logger.warning('Record.get_groups_with_records_for_subject(slug = %s, user_id = %d, group_type = %s) throws Student.DoesNotExist exception.' % (slug, user_id, group_type) )                 
                student_groups = {}
            for g in groups:
                g.limit = g.get_group_limit()
                g.classrooms = g.get_all_terms()
                g.enrolled = Record.number_of_students(g)
                if g in student_groups:
                    g.signed = True
        except Subject.DoesNotExist:
            logger.error('Record.get_groups_with_records_for_subject(slug = %s, user_id = %d, group_type = %s) throws Student.DoesNotExist exception.' % (slug, user_id, group_type) )                 
            raise NonSubjectException()
        return groups
    
    @staticmethod
    def get_students_in_group(group_id):
        try:
            group = Group.objects.get(id=group_id)
            return map(lambda x: x.student, Record.enrolled.filter(group=group))
        except Group.DoesNotExist:
            logger.error('Record.get_students_in_group(group_id = %d) throws Group.DoesNotExist exception.' % group_id )           
            raise NonGroupException()
    
    @staticmethod
    def get_groups_for_student(user_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            return map(lambda x: x.group, Record.enrolled.filter(student=student))
        except Student.DoesNotExist:
            logger.error('Record.get_groups_for_student(user_id = %d) throws Student.DoesNotExist exception.' % user_id )           
            raise NonStudentException()
    
    @staticmethod
    def is_student_in_subject_group_type(user_id, slug, group_type):
        try:
            User.objects.get(id=user_id).student
            subject = Subject.objects.get(slug=slug)
            user_subject_group_type = [g.id for g in Record.get_groups_for_student(user_id) if g.subject == subject and g.type == group_type]
            if user_subject_group_type:
                return user_subject_group_type[0]
            return False
        except Student.DoesNotExist:
            logger.error('Record.is_student_in_subject_group_type(slug = %s, user_id = %d, group_type = %s) throws Student.DoesNotExist exception.' % (slug, user_id, group_type))           
            raise NonStudentException()
        except Subject.DoesNotExist:
            logger.error('Record.is_student_in_subject_group_type(slug = %s, user_id = %d, group_type = %s) throws Subject.DoesNotExist exception.' % (slug, user_id, group_type) )           
            raise NonSubjectException()

    @staticmethod
    def pin_student_to_group(user_id, group_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            record, is_created = Record.objects.get_or_create(group=group, student=student, status=STATUS_PINNED)
            if is_created == False:            
                logger.error('Record.pin_student_to_group(user_id = %d, group_id = %d) raised AlreadyPinnedException exception.' % (user_id, group_id) )           
                raise AlreadyPinnedException()
            return record
        except Student.DoesNotExist:
            logger.error('Record.pin_student_to_group(user_id = %d, group_id = %d) throws Student.DoesNotExists exception.' % (user_id, group_id) )           
            raise NonStudentException()
        except Group.DoesNotExist: 
            logger.error('Record.pin_student_to_group(user_id = %d, group_id = %d) throws Group.DoesNotExists exception.' % (user_id, group_id) )           
            raise NonGroupException()

    @staticmethod
    def unpin_student_from_group(user_id, group_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            record = Record.objects.get(group=group, student=student, status=STATUS_PINNED)
            logger.info('User (%s) is not yet pinned to group (%d - [%s])' % (user.get_full_name(), group_id, str(group)) )           
            record.delete()
            return record
        except Record.DoesNotExist:
            logger.error('Record.unpin_student_from_group(user_id = %d, group_id = %d) throws Record.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (user_id, group_id) )           
            raise AlreadyNotPinnedException()
        except Student.DoesNotExist:
            logger.error('Record.unpin_student_from_group(user_id = %d, group_id = %d) throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (user_id, group_id) )           
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Record.unpin_student_from_group(user_id = %d, group_id = %d) throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (user_id, group_id) )           
            raise NonGroupException()

    @staticmethod
    def add_student_to_group(user_id, group_id):
        """ assignes student to group if his records for subject are open. If student is pinned to group, pinned becomes enrolled """
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            if not group.subject.is_recording_open_for_student(student):
                logger.warning('Record.add_student_to_group(user_id = %d, group_id = %d) raised RecordsNotOpenException exception.' % (user_id, group_id) )           
                raise RecordsNotOpenException()
            if Record.number_of_students(group=group) < group.limit:
                if (Record.is_student_in_subject_group_type(user_id=user.id, slug=group.subject_slug(), group_type=group.type) and group.type != '1'):
                    logger.warning('Record.add_student_to_group(user_id = %d, group_id = %d) raised AssignedInThisTypeGroupException exception.' % (user_id, group_id) )           
                    raise AssignedInThisTypeGroupException() #TODO: distinguish with AlreadyAssignedException 
                
                record = Record.objects.get(group=group, student=student)
                
                if record.status == STATUS_ENROLLED:
                    raise AlreadyAssignedException()
                             
                record.status = STATUS_ENROLLED
                record.save()
                
            else:
                logger.warning('Record.add_student_to_group() raised OutOfLimitException exception (parameters: user_id = %d, group_id = %d)' % (user_id, group_id) )           
                raise OutOfLimitException()
            return record
        except NonStudentOptionsException:
            logger.error('Record.add_student_to_group()  throws NonStudentOptionsException exception (parameters: user_id = %d, group_id = %d)' % (user_id, group_id) )           
            raise RecordsNotOpenException()
        except Student.DoesNotExist:
            logger.error('Record.add_student_to_group()  throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (user_id, group_id) ) 
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Record.add_student_to_group()  throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (user_id, group_id) ) 
            raise NonGroupException()
        except Record.DoesNotExist:
            logger.error('Record.add_student_to_group()  throws Record.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (user_id, group_id) ) 
            return Record.objects.create(group=group, student=student, status=STATUS_ENROLLED)

    @staticmethod
    def change_student_group(user_id, old_id, new_id):
        """ Deletes old student record and returns new record with changed group. """
        user = User.objects.get(id=user_id)
        try:
            student = user.student  
            old_group = Group.objects.get(id=old_id)
            new_group = Group.objects.get(id=new_id)
            if not new_group.subject.is_recording_open_for_student(student):
                logger.warning('Record.change_student_group() raised RecordsNotOpenException exception (parameters: user_id = %d, old_id = %d, new_id = %d)' % (user_id, old_id, new_id) )           
                raise RecordsNotOpenException()
            if Record.number_of_students(group=new_group) < new_group.limit:
                record = Record.enrolled.get(group=old_group, student=student)
                record.delete()
                new_record = Record.objects.create(group=new_group, student=student, status=STATUS_ENROLLED)
                logger.info('User (%s) changed his group from [%s] to [%s] ' % (user.get_full_name(), old_group, new_group) )
            else:
                raise OutOfLimitException()
                logger.info('User (%s) tried to enroll to group [%s] but OutOfLimitException was raised' % user.get_full_name() )               
            return new_record   
        except Student.DoesNotExist:
            logger.error('Record.add_student_to_group(user_id = %d, old_id = %d, new_id = %d) throws Student.DoesNotExist exception.' % (user_id, old_id, new_id) ) 
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Record.add_student_to_group(user_id = %d, old_id = %d, new_id = %d) throws Group.DoesNotExist exception.' % (user_id, old_id, new_id) ) 
            raise NonGroupException()
        except Record.DoesNotExist:
            logger.error('Record.add_student_to_group(user_id = %d, old_id = %d, new_id = %d) throws Record.DoesNotExist exception.' % (user_id, old_id, new_id) ) 
            raise AlreadyNotAssignedException()
        
    @staticmethod
    def remove_student_from_group(user_id, group_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            record = Record.enrolled.get(group=group, student=student)
            record.delete()
            logger.info('User (%s) is now removed from group (%s) (parameters: user_id = %d, group_id = %d)' % (user.get_full_name(), str(group), user_id, group_id) ) 
            return record
        except Record.DoesNotExist:
            logger.error('Record.remove_student_from_group() throws Record.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (user_id, group_id) ) 
            raise AlreadyNotAssignedException()
        except Student.DoesNotExist:
            logger.error('Record.remove_student_from_group() throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (user_id, group_id) ) 
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Record.remove_student_from_group() throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (user_id, group_id) )  
            raise NonGroupException()

    def group_slug(self):
        return self.group.subject_slug()

    class Meta:
        verbose_name = 'zapis'
        verbose_name_plural = 'zapisy'
        unique_together = (('student', 'group'),)

    def __unicode__(self):
        return "%s (%s - %s)" % (self.group.subject, self.group.get_type_display(), self.group.get_teacher_full_name())
