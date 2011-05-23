#-*- coding: utf-8 -*-
from apps.enrollment.records.exceptions import NonGroupException
from apps.enrollment.records.exceptions import ECTS_Limit_Exception 
from apps.enrollment.records.exceptions import NotCurrentSemesterException

from apps.enrollment.courses.models.course import Course
from django.contrib.auth.models import User
from django.db import models

from apps.users.models import Student

from apps.enrollment.courses.models import Group
from apps.enrollment.courses.models import PointsOfCourses,\
                                        PointsOfCourseEntities
from apps.enrollment.records.exceptions import *
from apps.enrollment.courses.exceptions import NonCourseException

from datetime import datetime, timedelta, date
from itertools import cycle

from django.db.models import signals
#from django.dispatch import receiver
from settings import ECTS_LIMIT_DURATION, ECTS_LIMIT


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
    def recorded_students(students):
        """ Returns students with information about his/her records """

        recorded = Record.enrolled.distinct().\
                   values_list('student__user__id', flat=True).\
                   order_by('student__user__id')

        for student in students: # O(n^2) - da sie liniowo, jezeli posortujemy po id a nie nazwiskach
            student.recorded = student.id in recorded

        return students


    @staticmethod
    def number_of_students(group):
        """Returns number of students enrolled to particular group"""
        group_ = group
        return Record.enrolled.filter(group=group_).count()

    @staticmethod
    def get_student_records_ids(student, semester):
        records = Record.objects.\
            filter(student=student, group__course__semester=semester).\
            values_list('group__pk', 'status');
        pinned = []
        enrolled = []
        for record in records:
            if int(record[1]) == 1:
                enrolled.append(record[0])
            else:
                pinned.append(record[0])
        return {
            'enrolled': enrolled,
            'pinned': pinned,
            'queued': Queue.queued.filter(student=student,\
                      group__course__semester=semester).\
                      values_list('group__pk', flat=True)
        }

    @staticmethod
    def get_student_records_objects(student, semester):
        '''
            TODO: po wywaleniu get_student_records zmienić nazwę na właśnie tą
        '''
        return Record.objects.\
            filter(student=student, group__course__semester=semester).\
            select_related('group', 'group__course', 'group__course__entity',\
            'group__course__type');

    @staticmethod
    def get_student_enrolled_ids(student, semester):
        return Record.enrolled.\
            filter(student=student, group__course__semester=semester).\
            values_list('group__pk', flat=True)

    @staticmethod
    def get_student_records(student):
        '''
            TODO: DEPRECATED
        '''
        records = Record.enrolled.filter(student=student).\
            select_related('group', 'group__course', 'group__teacher',
                'group__teacher__user', 'group__term').\
                order_by('group__course__name')
        groups = [record.group for record in records]
        for group in groups:
            group.terms_ = group.get_all_terms() # za dużo zapytań
            group.course_ = group.course
        return groups

    @staticmethod
    def get_groups_with_records_for_course(slug, user_id, group_type):
        try:
            course = Course.objects.get(slug=slug)
            groups = Group.objects.filter(course=course).filter(type=group_type)
            try:
                student_groups = Record.get_groups_for_student(user_id)
            except NonStudentException:
                logger.warning('Record.get_groups_with_records_for_course(slug = %s, user_id = %d, group_type = %s) throws Student.DoesNotExist exception.' % (unicode(slug), int(user_id), unicode(group_type)))
                student_groups = {}
            for g in groups:
                g.priority = Queue.get_priority(user_id, g.id)
                g.limit = g.get_group_limit()
                g.classrooms = g.get_all_terms()
                g.enrolled = Record.number_of_students(g)
                g.queued = Queue.number_of_students(g)
                g.is_in_diff = Record.is_student_in_course_group_type(user_id=user_id, slug=slug, group_type=group_type)
                if g in student_groups:
                    g.signed = True
                if (g.enrolled >= g.limit):
                    g.is_full = True
                else:
                    g.is_full = False
        except Course.DoesNotExist:
            logger.error('Record.get_groups_with_records_for_course(slug = %s, user_id = %d, group_type = %s) throws Student.DoesNotExist exception.' % (unicode(slug), int(user_id), unicode(group_type)))
            raise NonCourseException()
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
    def is_student_in_course_group_type(user_id, slug, group_type):
        try:
            User.objects.get(id=user_id).student
            course = Course.objects.get(slug=slug)
            user_course_group_type = [g.id for g in Record.get_groups_for_student(user_id) if g.course == course and g.type == group_type]
            if user_course_group_type:
                return user_course_group_type[0]
            return False
        except Student.DoesNotExist:
            logger.error('Record.is_student_in_course_group_type(slug = %s, user_id = %d, group_type = %s) throws Student.DoesNotExist exception.' % (unicode(slug), int(user_id), unicode(group_type)))
            raise NonStudentException()
        except Course.DoesNotExist:
            logger.error('Record.is_student_in_course_group_type(slug = %s, user_id = %d, group_type = %s) throws Course.DoesNotExist exception.' % (unicode(slug), int(user_id), unicode(group_type)))
            raise NonCourseException()

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
            logger.error('Record.unpin_student_from_group(user_id = %d, group_id = %d) throws Record.DoesNotExist exception' % (int(user_id), int(group_id)))
            raise AlreadyNotPinnedException()
        except Student.DoesNotExist:
            logger.error('Record.unpin_student_from_group(user_id = %d, group_id = %d) throws Student.DoesNotExist exception' % (int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.error('Record.unpin_student_from_group(user_id = %d, group_id = %d) throws Group.DoesNotExist exception' % (int(user_id), int(group_id)))
            raise NonGroupException()

    @staticmethod
    def add_student_to_lecture_group(user_id, course_id):
        """ assignes student to lectures group for a given course """        
        user = User.objects.get(id=user_id)
        course = Course.objects.get(id=course_id) # using in logger
        try:
            student = user.student
            lectures = Group.objects.filter(course=course_id, type='1')
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
            logger.info('User %s <id: %s> is automaticaly added to lectures of Course: [%s] <id: %s>' % (user.username, user.id, course.name, course.id))
            return new_records
        except Student.DoesNotExist:
            logger.error('Record.add_student_to_lecture_group()  throws Student.DoesNotExist exception (parameters: user_id = %d, course_id = %d)' % (int(user_id), int(course_id)))
            raise NonStudentException()
        except Record.DoesNotExist:
            new_records.append(Record.objects.create(group=l, student=student, status=STATUS_ENROLLED))
            return new_records
          

    @staticmethod
    def add_student_to_group(user_id, group_id):
        """ assignes student to group if his records for course are open. If student is pinned to group, pinned becomes enrolled """
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            new_records = []
            if not group.course.is_recording_open_for_student(student):
                raise RecordsNotOpenException()
            # logger.warning('Record.add_student_to_group(user_id = %d, group_id = %d) raised RecordsNotOpenException exception.' % (int(user_id), int(group_id)) )
            if Record.number_of_students(group=group) < group.limit:
                g_id = Record.is_student_in_course_group_type(user_id=user.id, slug=group.course_slug(), group_type=group.type)
                if g_id and group.type != '1':
                    #logger.warning('Record.add_student_to_group(user_id = %d, group_id = %d) raised AssignedInThisTypeGroupException exception.' % (int(user_id), int(group_id)))
                    #raise AssignedInThisTypeGroupException() #TODO: distinguish with AlreadyAssignedException
                    Record.remove_student_from_group(user_id, g_id)

                if group.type != '1':
                    new_records.extend(Record.add_student_to_lecture_group(user_id, group.course.id))
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
    def remove_student_from_group(user_id, group_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            if group.type=='1':
                course = group.course
                records = Record.enrolled.filter(group__course=course, student=student).exclude(group__type='1')
                for r in records:
                    Record.remove_student_from_group(user_id, r.group.id)
            if not group.course.is_recording_open_for_student(student):
                raise RecordsNotOpenException()
            if not group.course.semester.is_current_semester():
            	raise NotCurrentSemesterException
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
        return self.group.course_slug()

    class Meta:
        verbose_name = 'zapis'
        verbose_name_plural = 'zapisy'
        unique_together = (('student', 'group'), )

    def __unicode__(self):
        return u"%s (%s - %s)" % (self.group.course, self.group.get_type_display(), self.group.get_teacher_full_name())

class QueueManager(models.Manager):
    def get_query_set(self):
        """ Returns only queued students. """
        return super(QueueManager, self).get_query_set()

def queue_priority(value):
    """ Controls range of priority"""
    if value <= 0 or value > 10:
        raise ValidationError(u'%s is not a priority' % value)

class Queue(models.Model):
    group   = models.ForeignKey(Group, verbose_name='grupa')
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
            if not Group.objects.get(id=group_id).course.\
                is_recording_open_for_student(student):
                raise RecordsNotOpenException()
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
    def remove_student_from_queue(user_id, group_id):
        """remove student from queue"""
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            if not group.course.is_recording_open_for_student(student):
                raise RecordsNotOpenException()
            if not group.course.semester.is_current_semester():
            	raise NotCurrentSemesterException
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
    def get_point(program,course):
      pos = PointsOfCourses.objects.filter(course=course, program=program).values()
      if not pos:
         point = PointsOfCourseEntities.objects.filter(entity = course.entity).values()
         if point:
            return point[0]["value"]
         else:
            return 0
      else:
         return pos[0]["value"]

    @staticmethod
    def is_ECTS_points_limit_exceeded(user_id, group_id):
      """check if the sum of ECTS points for every course student is enrolled on, exceeds limit"""
      try:

            group = Group.objects.get(id=group_id)
            """ Sprawdzenie, czy obowiązuje jeszcze limit ECTS"""
            if group.course.semester.records_opening + timedelta(days=ECTS_LIMIT_DURATION) < datetime.now():
                return False
            """ Obliczenie sumy punktów ECTS"""
            groups = Record.get_groups_for_student(user_id)
            courses = set([g.course for g in groups])
            program = User.objects.get(id=user_id).student.program
            points = Queue.get_point(program, group.course)
            ects = sum([Queue.get_point(program,course) for course in courses])
            if group.course not in courses:
                ects += Queue.get_point(program,group.course)
    	    """ Porównanie sumy z obowiązującym limitem"""

            if ects <= ECTS_LIMIT - points:
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
            course = Course.objects.get(slug = group.course_slug())
            """ Pobranie listy grup z tego samego przedmiotu i tego samego typu, na które próbuje się zapisać student"""
            queued_group = [g for g in Queue.get_groups_for_student(user_id) if g.course == course and g.type == group.type]
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
        return self.group.course_slug()

    class Meta:
        verbose_name = 'kolejka'
        verbose_name_plural = 'kolejki'
        unique_together = (('student', 'group'),)

    def __unicode__(self):
        return u"%s (%s - %s)" % (self.group.course, self.group.get_type_display(), self.group.get_teacher_full_name())

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
