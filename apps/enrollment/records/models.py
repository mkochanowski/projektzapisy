#-*- coding: utf-8 -*-
from apps.enrollment.records.exceptions import NonGroupException
from apps.enrollment.records.exceptions import ECTS_Limit_Exception

from apps.enrollment.subjects.models.subject import Subject
from django.contrib.auth.models import User
from django.db import models

from apps.users.models import Student

from apps.enrollment.subjects.models import *
from apps.enrollment.records.exceptions import *
from apps.enrollment.subjects.exceptions import NonSubjectException, NonStudentOptionsException

from itertools import cycle

from django.db import transaction

from django.db.models import signals
#from django.dispatch import receiver
from apps.enrollment.subjects.models.group import Group


STATUS_ENROLLED = '1'
STATUS_PINNED = '2'
STATUS_QUEUED = '1'
RECORD_STATUS = [(STATUS_ENROLLED, u'zapisany'), (STATUS_PINNED, u'oczekujący')]

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
    def get_student_all_detailed_records(user_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            records = Record.objects.filter(student=student).\
                select_related('group', 'group__subject').order_by('group__subject__name')
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
            logger.error('Record.get_student_all_detailed_records(user_id = %d) throws Student.DoesNotExist exception.' % int(user_id))
            raise NonStudentException()

    @staticmethod
    def get_student_all_detailed_enrollings(user_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            records = Record.enrolled.filter(student=student).\
                select_related('group', 'group__subject', 'group__teacher', 'group__teacher__user').order_by('group__subject__name')
            groups = [record.group for record in records]
            subjects = set([group.subject for group in groups])
            for group in groups:
                group.terms_ = group.get_all_terms() # TODO: generuje osobne zapytanie dla każdej grupy, powinno być pobierane w jednym
                group.subject_ = group.subject
            return groups
        except Student.DoesNotExist:
            logger.error('Record.get_student_all_detailed_enrollings(user_id = %d) throws Student.DoesNotExist exception.' % int(user_id))
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
                g.priority = Queue.get_priority(user_id, g.id)
                g.limit = g.get_group_limit()
                g.classrooms = g.get_all_terms()
                g.enrolled = Record.number_of_students(g)
                g.queued = Queue.number_of_students(g)
                g.is_in_diff = Record.is_student_in_subject_group_type(user_id=user_id, slug=slug, group_type=group_type)
                if g in student_groups:
                    g.signed = True
                if (g.enrolled >= g.limit):
                    g.is_full = True
                else:
                    g.is_full = False
        except Subject.DoesNotExist:
            logger.error('Record.get_groups_with_records_for_subject(slug = %s, user_id = %d, group_type = %s) throws Student.DoesNotExist exception.' % (unicode(slug), int(user_id), unicode(group_type)))
            raise NonSubjectException()
        return groups

    @staticmethod
    def get_students_in_group(group_id):
        try:
            group = Group.objects.get(id=group_id)
            return map(lambda x: x.student, Record.enrolled.filter(group=group).order_by('student__user__last_name','student__user__first_name'))
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
            logger.info('User %s <id: %s> is now pinned to group: "%s" <id: %s>' % (user.username, user.id, group, group.id))
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
            record.delete()
            logger.info('User %s <id: %s> is no longer pinned to group: "%s" <id: %s>' % (user.username, user.id, group, group.id))
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
    def add_student_to_lecture_group(user_id, subject_id):
        """ assignes student to lectures group for a given subject """        
        user = User.objects.get(id=user_id)
        subject = Subject.objects.get(id=subject_id) # using in logger
        try:
            student = user.student
            lectures = Group.objects.filter(subject=subject_id, type='1')
            groups = Record.get_groups_for_student(user_id)
            new_records = []
            for l in lectures:
                if (l not in groups) and (Record.number_of_students(group=l) < l.limit):
                    record = Record.objects.get(group=l, student=student)
                    if record: 
                        if record.status == STATUS_PINNED:
                            record.status = STATUS_ENROLLED
                            record.save()
                            new_records.append(record)
            logger.info('User %s <id: %s> is automaticaly added to lectures of Subject: [%s] <id: %s>' % (user.username, user.id, subject.name, subject.id))
            return new_records
        except Student.DoesNotExist:
            logger.error('Record.add_student_to_lecture_group()  throws Student.DoesNotExist exception (parameters: user_id = %d, subject_id = %d)' % (int(user_id), int(subject_id)))
            raise NonStudentException()
        except Record.DoesNotExist:
            new_records.append(Record.objects.create(group=l, student=student, status=STATUS_ENROLLED))
            return new_records
          

    @staticmethod
    @transaction.commit_on_success
    def add_student_to_group(user_id, group_id):
        """ assignes student to group if his records for subject are open. If student is pinned to group, pinned becomes enrolled """
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            new_records = []
            if not group.subject.is_recording_open_for_student(student):
                raise RecordsNotOpenException()
            # logger.warning('Record.add_student_to_group(user_id = %d, group_id = %d) raised RecordsNotOpenException exception.' % (int(user_id), int(group_id)) )
            if Record.number_of_students(group=group) < group.limit:
                g_id = Record.is_student_in_subject_group_type(user_id=user.id, slug=group.subject_slug(), group_type=group.type)
                if g_id and group.type != '1':
                    #logger.warning('Record.add_student_to_group(user_id = %d, group_id = %d) raised AssignedInThisTypeGroupException exception.' % (int(user_id), int(group_id)))
                    #raise AssignedInThisTypeGroupException() #TODO: distinguish with AlreadyAssignedException
                    Record.remove_student_from_group(user_id, g_id)

                if group.type != '1':
                    new_records.extend(Record.add_student_to_lecture_group(user_id, group.subject.id))
                if Queue.is_ECTS_points_limit_exceeded(user_id, group_id) :
                    raise ECTS_Limit_Exception()
                record = Record.objects.get(group=group, student=student)

                if record.status == STATUS_ENROLLED:
                    raise AlreadyAssignedException()

                record.status = STATUS_ENROLLED
                record.save()
                
                new_records.append(record)
                logger.info('User %s <id: %s> who has been pinned to group: [%s] <id: %s> is currently added to this group and no longer pinned.' % (user.username, user.id, group, group.id))
                return new_records
            else:
                logger.warning('Record.add_student_to_group() raised OutOfLimitException exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
                raise OutOfLimitException()
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
            new_records.append(Record.objects.create(group=group, student=student, status=STATUS_ENROLLED))
            logger.info('User %s <id: %s> is added to group: "%s" <id: %s>' % (user.username, user.id, group, group.id))     
            return new_records

    @staticmethod
    @transaction.commit_on_success
    def remove_student_from_group(user_id, group_id):
        user = User.objects.get(id=user_id)
        try:

            student = user.student
            group = Group.objects.get(id=group_id)
            record = Record.enrolled.get(group=group, student=student)
            queued = Queue.remove_first_student_from_queue(group_id)
            record.delete()
            logger.info('User %s <id: %s> is removed from group: "%s" <id: %s>' % (user.username, user.id, group, group.id)) 
            if queued and (Record.number_of_students(group=group) < group.limit) :
                new_student = queued.student
                Record.add_student_to_group(new_student.user.id, group_id)
                Queue.remove_student_low_priority_records(new_student.user.id, group_id, queued.priority)
                logger.info('User %s <id: %s> replaced user %s <id: %s> in group [%s] <id: %s>.',  user.username, user.id, new_student.user.username, new_student.user.id, group, group.id)
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
        return super(QueueManager, self).get_query_set()

def queue_priority(value):
    """ Controls range of priority"""
    if value <= 0 or value > 10:
        raise ValidationError(u'%s is not a priority' % value)

class Queue(models.Model):
    group = models.ForeignKey(Group, verbose_name='grupa')
    student = models.ForeignKey(Student, verbose_name='student', related_name='queues')
    time = models.DateTimeField(verbose_name='Czas dołączenia do kolejki')
    priority = models.PositiveSmallIntegerField(default=1, validators=[queue_priority], verbose_name='priorytet')
    objects = models.Manager()
    queued = QueueManager()

    def set_priority(self, value):
        self.priority = value
        self.save()
        return self

    @staticmethod
    def number_of_students(group):
        """Returns number of students queued to particular group"""
        group_ = group
        return Queue.queued.filter(group=group_).count()

    @staticmethod
    def get_priority(user_id, group_id):
        """ Returns priority of student in group queue"""
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id = group_id)
            """Pobranie recordu z zapisem studenta do kolejki grupy"""
            queue = Queue.queued.filter(student=student, group=group)
            if queue:
                return queue[0].priority
            else:
                return False
        except Student.DoesNotExist:
            logger.error('Queue.get_priority() throws Student.DoesNotExist(parameters : user_id = %d, group_id = %d)' %(int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Queue.get_priority() throws Group.DoesNotExist(parameters : user_id = %d, group_id = %d)' %(int(user_id), int(group_id)))
            raise NonGroupException()


    @staticmethod
    def get_students_in_queue(group_id):
        """ Returns state of queue for group ordered by time (FIFO)."""
        try:
            group = Group.objects.get(id=group_id)
            return map(lambda x: x.student, Queue.queued.filter(group=group).order_by('time'))
        except Group.DoesNotExist:
            logger.error('Queue.get_students_in_queue() throws Group.DoesNotExist(parameters : group_id = %d)' % int(group_id))
            raise NonGroupException()

    @staticmethod
    def add_student_to_queue(user_id, group_id,priority=1):
        """ Assign student to queue"""
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            """ Czy student jest już zapisany na przedmiot"""
            if Record.enrolled.filter(group=group, student=student).count() > 0 :
                logger.warning('Queue.add_student_to_queue() throws AlreadyAssignedException() exception (parameters: user_id = %d, group_id = %d, priority = %d)' % (int(user_id), int(group_id), int(priority)))
                raise AlreadyAssignedException()
            """ Czy student nie jest już w danej kolejce"""
            if Queue.queued.filter(group=group, student=student).count() > 0 :
                logger.warning('Queue.add_student_to_queue() throws AlreadyQueuedException() exception (parameters: user_id = %d, group_id = %d, priority = %d)' % (int(user_id), int(group_id), int(priority)))
                raise AlreadyQueuedException()
            """ Próba utworzenia wpisu do kolejki"""
            record, is_created = Queue.objects.get_or_create(group=group, student=student, time=datetime.now(), priority=priority)
            if is_created == False: # Nie wiem czy ten warunek ma sens z tym powyżej
                logger.warning('Queue.add_student_to_queue() throws AlreadyQueuedException() exception (parameters: user_id = %d, group_id = %d, priority = %d)' % (int(user_id), int(group_id), int(priority)))
                raise AlreadyQueuedException()
            record.save()
            logger.info('User %s <id: %s> is added to queue of group "%s" <id: %s> with priority = %s' % (user.username, user.id, group, group_id, priority))
            return record
        except Student.DoesNotExist:
            logger.error('Queue.add_student_to_queue()  throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d, priority = %d)' % (int(user_id), int(group_id), int(priority)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Queue.add_student_to_queue()  throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d, priority = %d)' % (int(user_id), int(group_id), int(priority)))
            raise NonGroupException()

    @staticmethod
    def change_student_priority(user_id, group_id, new_priority) :
        """change student's priority in group queue"""
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            record = Queue.objects.get(group=group, student=student)
            """ Podstawienie nowej wartości"""
            record.priority = new_priority
            record.save()
            logger.info('User %s <id: %s> changed queue priority of group "%s" <id: %s> to %s' % (user.username, user.id, group, group.id, new_priority))
            return record
        except Queue.DoesNotExist:
            logger.error('Queue.change_student_priority() throws Queue.DoesNotExist exception (parameters: user_id = %d, group_id = %d, new_priority = %d)' % (int(user_id), int(group_id), int(new_priority)))
            raise AlreadyNotAssignedException()
        except Student.DoesNotExist:
            logger.error('Queue.add_student_to_queue()  throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d, new_priority = %d)' % (int(user_id), int(group_id), int(new_priority)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Queue.add_student_to_queue()  throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d, new_priority = %d)' % (int(user_id), int(group_id), int(new_priority)))
            raise NonGroupException()

    @staticmethod
    @transaction.commit_on_success
    def remove_student_from_queue(user_id, group_id):
        """remove student from queue"""
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            record = Queue.queued.get(group=group, student=student)
            record.delete()
            logger.info('User %s <id: %s> is now removed from queue of group "%s" <id: %s>' % (user.username, user.id, group, group.id)) 
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
    def is_ECTS_points_limit_exceeded(user_id, group_id):
      """check if the sum of ECTS points for every subject student is enrolled on, exceeds limit"""
      try:
            point_limit_duration = 14 # number of days from records openning when 40 ECTS point limit is in force TODO
            group = Group.objects.get(id=group_id)
            """ Sprawdzenie, czy obowiązuje jeszcze limit ECTS"""
            if group.subject.semester.records_opening + timedelta(days=point_limit_duration) < datetime.now():
		return False
            """ Obliczenie sumy punktów ECTS"""
            groups = Record.get_groups_for_student(user_id)
            subjects = set([g.subject for g in groups])
            ects = sum([s.ects for s in subjects])
            if group.subject not in subjects:
	        ects += group.subject.ects
	    """ Porównanie sumy z obowiązującym limitem"""
            if ects <= 40:
	        return False
	    else:
	        return True 
      except Student.DoesNotExist:
            logger.error('Queue.count_ECTS_points(user_id)  throws Student.DoesNotExist exception (parameters: user_id = %d)' % (int(user_id)))
            raise NonStudentException()


    @staticmethod
    def remove_first_student_from_queue(group_id):
        """return FIRST student from queue whose ECTS points limit is not excedeed, remove this student and all students
        before him from queue"""
        try:
            group = Group.objects.get(id=group_id)
            queue = Queue.queued.filter(group=group).order_by('time')
            """ Przeszukiwanie kolejki"""
            for q in queue:
                student_id = q.student.user.id
                """ Sprawdzenie mozliwosci zapisania studenta na zajęcia"""
                if Queue.is_ECTS_points_limit_exceeded(student_id, group_id):
                    """ Wyrzucenie studenta z kolejki. Jego limit ECTS nie pozwala zapisać go do grupy, na którą oczekuje"""
                    logger.info('User %s <id: %s> is now removed as first from queue of group "%s" <id %s> but he exceeded ECTS limit' % (q.student.user.username, q.student.user.id, group, group_id))
                    Queue.remove_student_from_queue(student_id, group_id)
                else:
                    logger.info('User %s <id: %s> is now removed as first from queue of group "%s" <id %s>' % (q.student.user.username, q.student.user.id, group, group_id))
                    return Queue.remove_student_from_queue(student_id, group_id)
            return False
        except Queue.DoesNotExist:
            logger.error('Queue.remove_first_student_from_queue() throws Queue.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise AlreadyNotAssignedException()
        except Student.DoesNotExist:
            logger.error('Queue.remove_first_student_from_group() throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Queue.remove_first_student_from_group() throws Group.DoesNotExist exception (parameters: group_id = %d)' % (int(group_id)))
            raise NonGroupException()
            
    @staticmethod
    def get_groups_for_student(user_id):
        """ Return all groups that student is trying to sign to."""
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
        user = User.objects.get(id = user_id)
        try :
            student = user.student
            group = Group.objects.get(id = group_id)
            subject = Subject.objects.get(slug = group.subject_slug())
            """ Pobranie listy grup z tego samego przedmiotu i tego samego typu, na które próbuje się zapisać student"""
            queued_group = [g for g in Queue.get_groups_for_student(user_id) if g.subject == subject and g.type == group.type]
            """ Usunięcie wszystkich wpisów z kolejki, które są na liście queued_group i posiadają niższy priorytet od zadanego"""
            for q_g in queued_group :
                record = Queue.queued.get(student = student,group = q_g)
                if (record.priority <= priority) :
                    logger.info('User %s <id: %s> is now removed from queue of group "%s" <id: %s> because of low priority (%s)' % (user.username, user.id, q_g, q_g.id, priority))
                    Queue.remove_student_from_queue(user_id,q_g.id)
        except Student.DoesNotExist:
            logger.error('Queue.remove_student_low_priority_records throws Student.DoesNotExist exception (parameters user_id = %d, group_id = %d, priority = %d)' % (int(user_id), int(group_id), int(priority)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Queue.remove_student_low_priority_records throws Group.DoesNotExist exception (parameters user_id = %d, group_id = %d, priority = %d)' % (int(user_id), int(group_id), int(priority)))
            raise NonGroupException()

    def group_slug(self):
        return self.group.subject_slug()

    class Meta:
        verbose_name = 'kolejka'
        verbose_name_plural = 'kolejki'
        unique_together = (('student', 'group'),)

    def __unicode__(self):
        return u"%s (%s - %s)" % (self.group.subject, self.group.get_type_display(), self.group.get_teacher_full_name())

def add_people_from_queue(sender, instance, **kwargs):
    """adding people from queue to group, after limits' change"""
    try:
        """ Pobranie liczby zapisanych studentów"""
        num_of_people = Record.objects.filter(group=instance).count()
        queued = True
        while queued and (num_of_people < instance.limit) :
            """ Opróżnianie kolejki do momentu osiągnięcia nowego limitu lub jej opróżnienia"""
            queued = Queue.remove_first_student_from_queue(instance.id)
            if queued:
                logger.info('User %s <id: %s> is now added to group "%s" <id: %s> because of limits\' change (parameters instance = %s)' % (queued.student.user.username, queued.student.user.id, queued.group, queued.group.id, instance.id)) #prosze o sprawdzenie, czy sie nie pomylilem                
                Record.add_student_to_group(queued.student.user.id, instance.id)
                num_of_people = Record.objects.filter(group=instance).count()
    except Queue.DoesNotExist:
        logger.error('Queue.add_people_from_queue throws Queue.DoesNotExist exception (parameters instance = %d)' % (int(instance.id)))
        raise AlreadyNotAssignedException()
    except Student.DoesNotExist:
        logger.error('Queue.add_people_from_queue throws Student.DoesNotExist exception (parameters instance = %d)' % (int(instance.id)))
        raise NonStudentException()
    except Group.DoesNotExist:
        logger.error('Queue.add_people_from_queue throws Group.DoesNotExist exception (parameters instance = %d)' % (int(instance.id)))
        raise NonGroupException()

signals.post_save.connect(add_people_from_queue, sender=Group)
