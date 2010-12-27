import Queue
#-*- coding: utf-8 -*-

from fereol.enrollment.subjects.models.subject import Subject
from django.contrib.auth.models import User
from django.db import models

from users.models import Student

from enrollment.subjects.models import *
from enrollment.records.exceptions import *
from enrollment.subjects.exceptions import NonSubjectException, NonStudentOptionsException

from itertools import cycle

from django.db import transaction

from django.db.models import signals
#from django.dispatch import receiver
from fereol.enrollment.subjects.models.group import Group


STATUS_ENROLLED = '1'
STATUS_PINNED = '2'
STATUS_QUEUED = '1'
RECORD_STATUS = [(STATUS_ENROLLED, u'zapisany'), (STATUS_PINNED, u'oczekujący')]

QUEUE_STATUS = [(STATUS_QUEUED, u'zakolejkowany'), (STATUS_PINNED, u'oczekujący')]

import logging
logger = logging.getLogger()

class EnrolledManager(models.Manager):
    def get_query_set(self):
        """ Returns only enrolled students. """
        return super(EnrolledManager, self).get_query_set().filter(status=STATUS_ENROLLED)

class Record(models.Model):
    group = models.ForeignKey(Group, verbose_name='grupa')
    student = models.ForeignKey(Student, verbose_name='student', related_name='records')
    status = models.CharField(max_length=1, choices=RECORD_STATUS, verbose_name='status')

    objects = models.Manager()
    enrolled = EnrolledManager()

    @staticmethod
    def number_of_students(group):
        """Returns number of students enrolled to particular group"""
        group_ = group
        return Record.enrolled.filter(group=group_).count()

    @staticmethod
    def get_student_all_detiled_records(user_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            records = Record.objects.filter(student=student).\
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
            logger.error('Record.get_student_all_detiled_records(user_id = %d) throws Student.DoesNotExist exception.' % int(user_id))
            raise NonStudentException()

    @staticmethod
    def get_student_all_detiled_enrollings(user_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            records = Record.enrolled.filter(student=student).\
                select_related('group', 'group__subject').order_by('group__subject')
            groups = [record.group for record in records]
            subjects = set([group.subject for group in groups])
            for group in groups:
                group.terms_ = group.get_all_terms()
                group.subject_ = group.subject
            return groups
        except Student.DoesNotExist:
            logger.error('Record.get_student_all_detiled_enrollings(user_id = %d) throws Student.DoesNotExist exception.' % int(user_id))
            raise NonStudentException()

    @staticmethod
    def get_groups_with_records_for_subject(slug, user_id, group_type):
        try:
            subject = Subject.objects.get(slug=slug)
            groups = Group.objects.filter(subject=subject).filter(type=group_type)
            try:
                student_groups = Record.get_groups_for_student(user_id)
            except NonStudentException:
                logger.warning('Record.get_groups_with_records_for_subject(slug = %s, user_id = %d, group_type = %s) throws Student.DoesNotExist exception.' % (unicode(slug), int(user_id), unicode(group_type)))
                student_groups = {}
            for g in groups:
                g.limit = g.get_group_limit()
                g.classrooms = g.get_all_terms()
                g.enrolled = Record.number_of_students(g)
                if g in student_groups:
                    g.signed = True
        except Subject.DoesNotExist:
            logger.error('Record.get_groups_with_records_for_subject(slug = %s, user_id = %d, group_type = %s) throws Student.DoesNotExist exception.' % (unicode(slug), int(user_id), unicode(group_type)))
            raise NonSubjectException()
        return groups

    @staticmethod
    def get_students_in_group(group_id):
        try:
            group = Group.objects.get(id=group_id)
            return map(lambda x: x.student, Record.enrolled.filter(group=group))
        except Group.DoesNotExist:
            raise NonGroupException()

    @staticmethod
    def get_groups_for_student(user_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            return map(lambda x: x.group, Record.enrolled.filter(student=student))
        except Student.DoesNotExist:
            logger.error('Record.get_groups_for_student(user_id = %d) throws Student.DoesNotExist exception.' % int(user_id))
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
            logger.error('Record.is_student_in_subject_group_type(slug = %s, user_id = %d, group_type = %s) throws Student.DoesNotExist exception.' % (unicode(slug), int(user_id), unicode(group_type)))
            raise NonStudentException()
        except Subject.DoesNotExist:
            logger.error('Record.is_student_in_subject_group_type(slug = %s, user_id = %d, group_type = %s) throws Subject.DoesNotExist exception.' % (unicode(slug), int(user_id), unicode(group_type)))
            raise NonSubjectException()

    @staticmethod
    def pin_student_to_group(user_id, group_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            record, is_created = Record.objects.get_or_create(group=group, student=student, status=STATUS_PINNED)
            if is_created == False:
                logger.error('Record.pin_student_to_group(user_id = %d, group_id = %d) raised AlreadyPinnedException exception.' % (int(user_id), int(group_id)))
                raise AlreadyPinnedException()
            return record
        except Student.DoesNotExist:
            logger.error('Record.pin_student_to_group(user_id = %d, group_id = %d) throws Student.DoesNotExists exception.' % (int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Record.pin_student_to_group(user_id = %d, group_id = %d) throws Group.DoesNotExists exception.' % (int(user_id), int(group_id)))
            raise NonGroupException()

    @staticmethod
    def unpin_student_from_group(user_id, group_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            record = Record.objects.get(group=group, student=student, status=STATUS_PINNED)
            logger.info('User (%s) is not yet pinned to group (%d - [%s])' % (user.get_full_name(), int(group_id), unicode(group)))
            record.delete()
            return record
        except Record.DoesNotExist:
            logger.error('Record.unpin_student_from_group(user_id = %d, group_id = %d) throws Record.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise AlreadyNotPinnedException()
        except Student.DoesNotExist:
            logger.error('Record.unpin_student_from_group(user_id = %d, group_id = %d) throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Record.unpin_student_from_group(user_id = %d, group_id = %d) throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonGroupException()

    @staticmethod
    def add_student_to_group(user_id, group_id):
        """ assignes student to group if his records for subject are open. If student is pinned to group, pinned becomes enrolled """
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            if not group.subject.is_recording_open_for_student(student):
                raise RecordsNotOpenException()
            # logger.warning('Record.add_student_to_group(user_id = %d, group_id = %d) raised RecordsNotOpenException exception.' % (int(user_id), int(group_id)) )
            if Record.number_of_students(group=group) < group.limit:
                if (Record.is_student_in_subject_group_type(user_id=user.id, slug=group.subject_slug(), group_type=group.type) and group.type != '1'):
                    logger.warning('Record.add_student_to_group(user_id = %d, group_id = %d) raised AssignedInThisTypeGroupException exception.' % (int(user_id), int(group_id)))
                    raise AssignedInThisTypeGroupException() #TODO: distinguish with AlreadyAssignedException

                record = Record.objects.get(group=group, student=student)

                if record.status == STATUS_ENROLLED:
                    raise AlreadyAssignedException()

                record.status = STATUS_ENROLLED
                record.save()
                if Queue.queued.filter(student=student, group=goup).count > 0 :
                    priority = Queue.queued.get(student=student, group=goup).priority
                    Queue.remove_student_low_priority_records(user_id, group_id, priority)
            else:
                logger.warning('Record.add_student_to_group() raised OutOfLimitException exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
                raise OutOfLimitException()
            logger.info('User %d is now added to group %d' % (int(user_id), int(group_id)))
            return record
        except NonStudentOptionsException:
            logger.error('Record.add_student_to_group()  throws NonStudentOptionsException exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise RecordsNotOpenException()
        except Student.DoesNotExist:
            logger.error('Record.add_student_to_group()  throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Record.add_student_to_group()  throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonGroupException()
        except Record.DoesNotExist:
            return Record.objects.create(group=group, student=student, status=STATUS_ENROLLED)

    @staticmethod
    @transaction.commit_on_success
    def remove_student_from_group(user_id, group_id):
        user = User.objects.get(id=user_id)
        try:

            student = user.student
            group = Group.objects.get(id=group_id)
            record = Record.enrolled.get(group=group, student=student)
            queued = Queue.remove_first_student_from_queue(group_id)
            logger.info('%s', (unicode(queued)))
                            # removing student from group + adding first from queue
            record.delete()
            if queued and (Record.number_of_students(group=group) < group.limit) :
                new_student = queued.student
                Record.add_student_to_group(new_student.user.id, group.id)
                logger.info('User (%s) replaced user (%s) in group [%s] ' % (user.get_full_name(), queued.student.get_full_name, unicode(group)))
                   
#czy można się zapisać na ten sam przedmiot - do kilku kolejek? otwarcie zapisów? ECTSy - jak przekracza, to wylatuje z kolejki, jak nie ma otwartych zapisów, to nie zapisuje się do kolejki; ostrzeżenie przy przypinaniu - ectsy; po otwarciu zapisów przypinanie staje się zapisem/zapisem do kolejki
            return record

        except Record.DoesNotExist:
            logger.error('Record.remove_student_from_group() throws Record.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise AlreadyNotAssignedException()
        except Student.DoesNotExist:
            logger.error('Record.remove_student_from_group() throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Record.remove_student_from_group() throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonGroupException()

    @staticmethod
    @transaction.commit_on_success
    def change_student_group(user_id, old_id, new_id):
        """ Deletes old student record and returns new record with changed group. """
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            old_group = Group.objects.get(id=old_id)
            new_group = Group.objects.get(id=new_id)
            if not new_group.subject.is_recording_open_for_student(student):
                logger.warning('Record.change_student_group() raised RecordsNotOpenException exception (parameters: user_id = %d, old_id = %d, new_id = %d)' % (int(user_id), int(old_id), int(new_id)))
                raise RecordsNotOpenException()
            if Record.number_of_students(group=new_group) < new_group.limit:
                Record.remove_student_from_group(user_id, old_id)
                new_record = Record.add_student_to_group(user_id, new_id)
                logger.info('User (%s) changed his group from [%s] to [%s] ' % (user.get_full_name(), unicode(old_group), unicode(new_group)))
            else:
                raise OutOfLimitException()
                logger.info('User (%s) tried to enroll to group [%s] but OutOfLimitException was raised' % user.get_full_name())
            return new_record
        except Student.DoesNotExist:
            logger.error('Record.add_student_to_group(user_id = %d, old_id = %d, new_id = %d) throws Student.DoesNotExist exception.' % (int(user_id), int(old_id), int(new_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Record.add_student_to_group(user_id = %d, old_id = %d, new_id = %d) throws Group.DoesNotExist exception.' % (int(user_id), int(old_id), int(new_id)))
            raise NonGroupException()
        except Record.DoesNotExist:
            logger.error('Record.add_student_to_group(user_id = %d, old_id = %d, new_id = %d) throws Record.DoesNotExist exception.' % (int(user_id), int(old_id), int(new_id)))
            raise AlreadyNotAssignedException()



    def group_slug(self):
        return self.group.subject_slug()

    class Meta:
        verbose_name = 'zapis'
        verbose_name_plural = 'zapisy'
        unique_together = (('student', 'group'), )

    def __unicode__(self):
        return u"%s (%s - %s)" % (self.group.subject, self.group.get_type_display(), self.group.get_teacher_full_name())

class QueueManager(models.Manager):
    def get_query_set(self):
        """ Returns only queued students. """
        return super(QueueManager, self).get_query_set().filter(status=STATUS_QUEUED)

class Queue(models.Model):
    group = models.ForeignKey(Group, verbose_name='grupa')
    student = models.ForeignKey(Student, verbose_name='student', related_name='queues')
    status = models.CharField(max_length=1, choices=QUEUE_STATUS, verbose_name='status')
    time = models.DateTimeField(verbose_name='Czas dołączenia do kolejki')
    priority = models.PositiveSmallIntegerField(default=0, verbose_name='priorytet')
    objects = models.Manager()
    queued = QueueManager()

    @staticmethod
    def get_students_in_queue(group_id):
        try:
            group = Group.objects.get(id=group_id)
            return map(lambda x: x.student, Queue.queued.filter(group=group))
        except Group.DoesNotExist:
            raise NonGroupException()

    @staticmethod
    def add_student_to_queue(user_id, group_id,priority=0):
        """ assignes student to queue."""
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            if Record.enrolled.filter(group=group, student=student).count() > 0 :
                logger.error('Queue.add_student_to_queue(user_id = %d, group_id = %d) raised AlreadyAssignedException exception.' % (int(user_id), int(group_id)))
                raise AlreadyAssignedException()
            if Queue.queued.filter(group=group, student=student).count() > 0 :
                logger.error('Queue.add_student_to_queue(user_id = %d, group_id = %d) raised AlreadyQueuedException exception.' % (int(user_id), int(group_id)))
                raise AlreadyQueuedException()
            record, is_created = Queue.objects.get_or_create(group=group, student=student, status=STATUS_QUEUED, time=datetime.now(), priority=priority)
            if is_created == False: # Nie wiem czy ten warunek ma sens z tym powyżej
                logger.error('Queue.add_student_to_queue(user_id = %d, group_id = %d) raised AlreadyQueuedException exception.' % (int(user_id), int(group_id)))
                raise AlreadyQueuedException()
            record.save()

            return record
        except Student.DoesNotExist:
            logger.error('Queue.add_student_to_queue()  throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Queue.add_student_to_queue()  throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonGroupException()

    @staticmethod
    def change_student_priority(user_id, group_id, priority) :
        """change student priority in group queue"""
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            record = Queue.objects.get(group=group, student=student, status=STATUS_QUEUED)
            record.priority = priority
            record.save()
            return record
        except Queue.DoesNotExist:
            logger.error('Queue.change_student_priority() throws Queue.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise AlreadyNotAssignedException()
        except Student.DoesNotExist:
            logger.error('Queue.add_student_to_queue()  throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Queue.add_student_to_queue()  throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonGroupException()

    @staticmethod
    def remove_student_from_queue(user_id, group_id):
        """remove student from queue"""
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            record = Queue.queued.get(group=group, student=student)
            record.delete()
            logger.info('User (%s) is now removed from queue to group (%s) (parameters: user_id = %d, group_id = %d)' % (user.get_full_name(), unicode(group), int(user_id), int(group_id)))
            return record
        except Queue.DoesNotExist:
            logger.error('Queue.remove_student_from_queue() throws Queue.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise AlreadyNotAssignedException()
        except Student.DoesNotExist:
            logger.error('Queue.remove_student_from_group() throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Queue.remove_student_from_group() throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonGroupException()

    @staticmethod
    def remove_first_student_from_queue(group_id):
        """remove FIRST student from queue"""
        try:
            group = Group.objects.get(id=group_id)
            queue = Queue.objects.filter(group=group).order_by('time')
            if queue :
                first = queue[0]
                student_id = first.student.user.id
                return Queue.remove_student_from_queue(student_id, group_id)
            else :
                return False
        except Queue.DoesNotExist:
            logger.error('Queue.remove_first_student_from_queue() throws Queue.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise AlreadyNotAssignedException()
        except Student.DoesNotExist:
            logger.error('Queue.remove_first_student_from_group() throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Queue.remove_first_student_from_group() throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonGroupException()
            
    @staticmethod
    def get_groups_for_student(user_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            return map(lambda x: x.group, Queue.queued.filter(student=student))
        except Student.DoesNotExist:
            logger.error('Queue.get_groups_for_student(user_id = %d) throws Student.DoesNotExist exception.' % int(user_id))
            raise NonStudentException()

    @staticmethod
    def remove_student_low_priority_records(user_id, group_id, priority) :
        """ Funkcja, która czyści kolejkę z wpisów do grup z tego samego przedmiotu o tym samym rodzaju ale mniejszym priorytecie"""
        try :
            student = User.objects.get(id = user_id).student
            group = Group.objects.get(id = group_id)
            subject = Subject.objects.get(slug = group.subject_slug())
            queued_group = [g for g in Queue.get_groups_for_student(user_id) if g.subject == subject and g.type == group.type]
            for q_g in queued_group :
                record = Queue.queued.get(student = student,group = q_g)
                if (record.priority <= priority) :
                    Queue.remove_student_from_queue(user_id,q_g.id)
        except Student.DoesNotExist:
            logger.error('Queue.remove_student_low_priority_records throws Student.DoesNotExist exception (parameters user_id = %d, group_id = %d, priority = %d)' % int(user_id), int(group_id), int(priority))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Queue.remove_student_low_priority_records throws Group.DoesNotExist exception (parameters user_id = %d, group_id = %d, priority = %d)' % int(user_id), int(group_id), int(priority))
            raise NonGroupException()

    class Meta:
        verbose_name = 'kolejka'
        verbose_name_plural = 'kolejki'
        unique_together = (('student', 'group'),)

    def __unicode__(self):
        return u"%s (%s - %s)" % (self.group.subject, self.group.get_type_display(), self.group.get_teacher_full_name())

#adding people from queue to group, after limits' change

#@receiver(post_save, sender=Group)
def add_people_from_queue(sender, instance, **kwargs):
    num_of_people = Record.objects.filter(group=instance).count()
    queued = True
    while queued and (num_of_people < instance.limit) :
        queued = Queue.remove_first_student_from_queue(instance.id)
        if queued :
            Record.add_student_to_group(queued.student.user.id, instance.id)
            num_of_people = Record.objects.filter(group=instance).count()

signals.post_save.connect(add_people_from_queue, sender=Group)
