#-*- coding: utf-8 -*-
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from apps.enrollment.records.exceptions import NonGroupException
from apps.enrollment.records.exceptions import ECTS_Limit_Exception 
from apps.enrollment.records.exceptions import InactiveStudentException

from apps.enrollment.courses.models.course import Course
from apps.enrollment.courses.models.group  import Group
from apps.enrollment.courses.models.semester  import Semester

from django.contrib.auth.models import User
from django.db import models

from apps.users.models import Student

from apps.enrollment.records.exceptions import *
from apps.enrollment.courses.exceptions import NonCourseException

from datetime import datetime, timedelta, date
from itertools import cycle

from django.db.models import signals
#from django.dispatch import receiver
from settings import ECTS_LIMIT

from apps.enrollment.utils import mail_enrollment_from_queue

STATUS_ENROLLED = '1'
STATUS_PINNED = '2'
STATUS_QUEUED = '1'
RECORD_STATUS = [(STATUS_ENROLLED, u'zapisany'), (STATUS_PINNED, u'przypięty')]

import logging
logger = logging.getLogger('project.default')
backup_logger = logging.getLogger('project.backup')

class EnrolledManager(models.Manager):
    def get_query_set(self):
        """ Returns only enrolled students. """
        return super(EnrolledManager, self).get_query_set().filter(status=STATUS_ENROLLED)

class PinnedManager(models.Manager):
    def get_query_set(self):
        """ Returns only enrolled students. """
        return super(PinnedManager, self).get_query_set().filter(status=STATUS_PINNED)

class Record(models.Model):
    group = models.ForeignKey(Group, verbose_name='grupa')
    student = models.ForeignKey(Student, verbose_name='student', related_name='records')
    status = models.CharField(max_length=1, choices=RECORD_STATUS, verbose_name='status')
    
    objects = models.Manager()
    enrolled = EnrolledManager()
    pinned = PinnedManager()
    
    def get_semester_name(self):
        return self.group.course.semester.get_name()
    
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
    def get_student_enrolled_objects(student, semester):
        '''
            TODO: po wywaleniu get_student_records zmienić nazwę na właśnie tą
        '''
        return Record.enrolled.\
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
        user = User.objects.get(id=user_id)
        try:
            course = Course.objects.get(slug=slug)
            groups = Group.objects.filter(course=course).filter(type=group_type)
            try:
                student_groups = Record.get_groups_for_student(user)
            except NonStudentException:
                logger.warning('Record.get_groups_with_records_for_course(slug = %s, user_id = %d, group_type = %s) throws Student.DoesNotExist exception.' % (unicode(slug), int(user_id), unicode(group_type)))
                student_groups = {}
            for g in groups:
                g.priority = Queue.get_priority(user_id, g.id)
                g.limit = g.get_group_limit()
                g.classrooms = g.get_all_terms()
                g.enrolled = g.get_count_of_enrolled()
                g.queued = g.get_count_of_queued()
                g.is_in_diff = Record.is_student_in_course_group_type(user=user, slug=slug, group_type=group_type)
                if g in student_groups:
                    g.signed = True
                if g.enrolled < g.limit:
                    g.is_full = False
                else:
                    g.is_full = True
        except Course.DoesNotExist:
            logger.warning('Record.get_groups_with_records_for_course(slug = %s, user_id = %d, group_type = %s) throws Student.DoesNotExist exception.' % (unicode(slug), int(user_id), unicode(group_type)))
            raise NonCourseException()
        return groups
    
    @staticmethod
    def get_students_in_group(group_id):
        try:
            return Student.objects.filter(records__group_id=group_id, records__status=1).select_related('user')
        except Group.DoesNotExist:
            raise NonGroupException()
    
    @staticmethod
    def get_groups_for_student(user):
        try:
            student = user.student
            return map(lambda x: x.group, \
                Record.enrolled.filter(student=student).\
                select_related('group', 'group__course'))
        except Student.DoesNotExist:
            logger.warning('Record.get_groups_for_student(user_id = %d) throws Student.DoesNotExist exception.' % int(user.id))
            raise NonStudentException()
    
    @staticmethod
    def is_student_in_course_group_type(user, slug, group_type):
        try:
            course = Course.objects.get(slug=slug)
            user_course_group_type = [g.id for g in Record.get_groups_for_student(user) if g.course == course and g.type == group_type]
            if user_course_group_type:
                return user_course_group_type[0]
            return False
        except Student.DoesNotExist:
            logger.warning('Record.is_student_in_course_group_type(slug = %s, user_id = %d, group_type = %s) throws Student.DoesNotExist exception.' % (unicode(slug), int(user.id), unicode(group_type)))
            raise NonStudentException()
        except Course.DoesNotExist:
            logger.warning('Record.is_student_in_course_group_type(slug = %s, user_id = %d, group_type = %s) throws Course.DoesNotExist exception.' % (unicode(slug), int(user.id), unicode(group_type)))
            raise NonCourseException()
    
    @staticmethod
    def pin_student_to_group(user_id, group_id):
        user = User.objects.get(id=user_id)
        try:
            student = user.student
            group = Group.objects.get(id=group_id)
            record, is_created = Record.objects.get_or_create(group=group, student=student, status=STATUS_PINNED)
            if is_created == False:
                logger.warning('Record.pin_student_to_group(user_id = %d, group_id = %d) raised AlreadyPinnedException exception.' % (int(user_id), int(group_id)))
                raise AlreadyPinnedException()
            logger.info('User %s <id: %s> is now pinned to group: "%s" <id: %s>' % (user.username, user.id, group, group.id))
            return record
        except Student.DoesNotExist:
            logger.warning('Record.pin_student_to_group(user_id = %d, group_id = %d) throws Student.DoesNotExists exception.' % (int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.warning('Record.pin_student_to_group(user_id = %d, group_id = %d) throws Group.DoesNotExists exception.' % (int(user_id), int(group_id)))
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
            logger.warning('Record.unpin_student_from_group(user_id = %d, group_id = %d) throws Record.DoesNotExist exception' % (int(user_id), int(group_id)))
            raise AlreadyNotPinnedException()
        except Student.DoesNotExist:
            logger.warning('Record.unpin_student_from_group(user_id = %d, group_id = %d) throws Student.DoesNotExist exception' % (int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.warning('Record.unpin_student_from_group(user_id = %d, group_id = %d) throws Group.DoesNotExist exception' % (int(user_id), int(group_id)))
            raise NonGroupException()
    
    @staticmethod
    def add_student_to_lecture_group(user, course):
        """ assignes student to lectures group for a given course """
        try:
            student = user.student
            lectures = Group.objects.filter(course=course, type__in=['1','9'])
            groups = Record.get_groups_for_student(user)
            new_records = []
            for l in lectures:
                #TODO: nie podoba mi się to
                if (l not in groups) and (l.get_count_of_enrolled(dont_use_cache=False) < l.limit):
                    record, created = Record.objects.get_or_create(group=l, student=student)
                    if created:
                        record.status = STATUS_ENROLLED
                        record.save()
                    elif record.status == STATUS_PINNED:
                            record.status = STATUS_ENROLLED
                            record.save()
                    new_records.append(record)
                    try:
                        queued = Queue.queued.get(group=l, student=student)
                        queued.delete()
                    except Queue.DoesNotExist:
                        pass
                    logger.info('User %s <id: %s> is automaticaly added to lecture <id: %s> of Course: [%s] <id: %s>' % (user.username, user.id, l.id, course.name, course.id))
                    backup_logger.info('[02] user <%s> is automaticaly added to lecture group <%s>' % (user.id, l.id))
            return new_records
        except Student.DoesNotExist:
            logger.warning('Record.add_student_to_lecture_group()  throws Student.DoesNotExist exception (parameters: user_id = %d, course_id = %d)' % (int(user.id), int(course.id)))
            raise NonStudentException()
          
    
    @staticmethod
    def add_student_to_group(user, group):
        """ assignes student to group if his records for course are open. If student is pinned to group, pinned becomes enrolled """
        try:
            student = user.student
            if not student.is_active():
                raise InactiveStudentException
            new_records = []
            if not group.course.is_recording_open_for_student(student):
                raise RecordsNotOpenException()
            # logger.warning('Record.add_student_to_group(user_id = %d, group_id = %d) raised RecordsNotOpenException exception.' % (int(user_id), int(group_id)) )
            if (group.limit_zamawiane > 0 and not student.is_zamawiany()):
                group_is_full = group.get_count_of_enrolled_non_zamawiane(dont_use_cache=False) >= group.limit_non_zamawiane()
            else:
                group_is_full = group.get_count_of_enrolled(dont_use_cache=False) >= group.limit
            if not group_is_full:
                g_id = Record.is_student_in_course_group_type(user=user, slug=group.course_slug(), group_type=group.type)
                if g_id and group.type != '1':
                    #logger.warning('Record.add_student_to_group(user_id = %d, group_id = %d) raised AssignedInThisTypeGroupException exception.' % (int(user_id), int(group_id)))
                    #raise AssignedInThisTypeGroupException() #TODO: distinguish with AlreadyAssignedException
                    group_rem = Group.objects.filter(id=g_id).select_related('course', 'course__semester').get()
                    Record.remove_student_from_group(user, group_rem)
                
                if Queue.is_ECTS_points_limit_exceeded(user, group) :
                    raise ECTS_Limit_Exception()
                if group.type != '1':
                    new_records.extend(Record.add_student_to_lecture_group(user, group.course))
                record, created = Record.objects.get_or_create(group=group, student=student)
    
                if not created:
                    if record.status == STATUS_ENROLLED:
                        raise AlreadyAssignedException()
                
                record.status = STATUS_ENROLLED
                record.save()
                #backup_logger.info('[01] user <%s> is added to group <%s>' % (user.id, group.id))
                new_records.append(record)
                if created:
                    logger.info('User %s <id: %s> is added to group: "%s" <id: %s>' % (user.username, user.id, group, group.id))                     
                else:
                    logger.info('User %s <id: %s> who has been pinned to group: [%s] <id: %s> is currently added to this group and no longer pinned.' % (user.username, user.id, group, group.id))
                return new_records
            else:
                logger.warning('Record.add_student_to_group() raised OutOfLimitException exception (parameters: user_id = %d, group_id = %d)' % (int(user.id), int(group.id)))
                raise OutOfLimitException()
        except Student.DoesNotExist:
            logger.warning('Record.add_student_to_group()  throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user.id), int(group.id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.warning('Record.add_student_to_group()  throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user.id), int(group.id)))
            raise NonGroupException()
    
    @staticmethod
    def remove_student_from_group(user, group):
        try:
            student = user.student
            if group.type=='1':
                course = group.course
                records = Record.enrolled.filter(group__course=course, student=student).exclude(group__type='1')
                for r in records:
                    Record.remove_student_from_group(user, r.group)
            if not group.course.is_recording_open_for_student(student):
                raise RecordsNotOpenException()
            record = Record.enrolled.get(group=group, student=student)
            record.delete()
            #backup_logger.info('[03] user <%s> is removed from group <%s>' % (user.id, group.id))
            logger.info('User %s <id: %s> is removed from group: "%s" <id: %s>' % (user.username, user.id, group, group.id))
            
            Queue.try_enroll_next_student(group) #TODO: być może zbędne
            
            return record
            
        except Record.DoesNotExist:
            logger.warning('Record.remove_student_from_group() throws Record.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user.id), int(group.id)))
            raise AlreadyNotAssignedException()
        except Student.DoesNotExist:
            logger.warning('Record.remove_student_from_group() throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user.id), int(group.id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.warning('Record.remove_student_from_group() throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user.id), int(group.id)))
            raise NonGroupException()

    @staticmethod
    def on_student_remove_from_group(sender, instance, **kwargs):
        try:
            group = instance.group
            if group.course.semester.records_opening <= datetime.now() < group.course.semester.records_closing:
                Queue.try_enroll_next_student(group)
                instance.group.update_students_counts()
        except ObjectDoesNotExist:
            pass
    
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
    def get_student_queues(student, semester):
        return Queue.queued.filter(student=student,
            group__course__semester=semester)
#        for queue in raw:
#            queues[queue.id] = queue
#        return queues

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
            logger.warning('Queue.get_priority() throws Student.DoesNotExist(parameters : user_id = %d, group_id = %d)' %(int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.warning('Queue.get_priority() throws Group.DoesNotExist(parameters : user_id = %d, group_id = %d)' %(int(user_id), int(group_id)))
            raise NonGroupException()
            
    
    @staticmethod
    def get_students_in_queue(group_id):
        """ Returns state of queue for group ordered by time (FIFO)."""
        try:
            return Student.objects.filter(queues__group_id=group_id).select_related('user').order_by('queues__time')
        except Group.DoesNotExist:
            logger.warning('Queue.get_students_in_queue() throws Group.DoesNotExist(parameters : group_id = %d)' % int(group_id))
            raise NonGroupException()
    
    @staticmethod
    def add_student_to_queue(user_id, group_id,priority=1):
        """ Assign student to queue"""
        try:
            student = Student.objects.select_related('user').get(user__id=user_id)
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
            logger.info('User %s <id: %s> is added to queue of group "%s" <id: %s> with priority = %s' % (student.user.username, student.user.id, group, group_id, priority))
            return record
        except Student.DoesNotExist:
            logger.warning('Queue.add_student_to_queue()  throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d, priority = %d)' % (int(user_id), int(group_id), int(priority)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.warning('Queue.add_student_to_queue()  throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d, priority = %d)' % (int(user_id), int(group_id), int(priority)))
            raise NonGroupException()
    
    @staticmethod
    def change_student_priority(user_id, group_id, new_priority) :
        """change student's priority in group queue"""
        try:
            student = Student.objects.select_related('user').get(user__id=user_id)
            record = Queue.objects.select_related('group').get(student=student, group__id=group_id)
            """ Podstawienie nowej wartości"""
            record.priority = new_priority
            record.save()
            logger.info('User %s <id: %s> changed queue priority of group "%s" <id: %s> to %s' % (student.user.username, student.user.id, record.group, record.group.id, new_priority))
            return record
        except Queue.DoesNotExist:
            logger.warning('Queue.change_student_priority() throws Queue.DoesNotExist exception (parameters: user_id = %d, group_id = %d, new_priority = %d)' % (int(user_id), int(group_id), int(new_priority)))
            raise AlreadyNotAssignedException()
        except Student.DoesNotExist:
            logger.warning('Queue.add_student_to_queue()  throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d, new_priority = %d)' % (int(user_id), int(group_id), int(new_priority)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.warning('Queue.add_student_to_queue()  throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d, new_priority = %d)' % (int(user_id), int(group_id), int(new_priority)))
            raise NonGroupException()
    
    @staticmethod
    def remove_student_from_queue(user_id, group_id):
        """remove student from queue"""
        try:
            student = Student.objects.select_related('user').get(user__id=user_id)

            record = Queue.queued.select_related('group').get(group__id=group_id, student=student)
            group = record.group
            if not group.course.is_recording_open_for_student(student):
                raise RecordsNotOpenException()
            record.delete()
            logger.info('User %s <id: %s> is now removed from queue of group "%s" <id: %s>' % (student.user.username, student.user.id, group, group.id))
            return record
        except Queue.DoesNotExist:
            logger.warning('Queue.remove_student_from_queue() throws Queue.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise AlreadyNotAssignedException()
        except Student.DoesNotExist:
            logger.warning('Queue.remove_student_from_group() throws Student.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.warning('Queue.remove_student_from_group() throws Group.DoesNotExist exception (parameters: user_id = %d, group_id = %d)' % (int(user_id), int(group_id)))
            raise NonGroupException()
    
    @staticmethod
    def get_point(program, course, student=None):
      """
          TODO: OMFG, to nie powinno być w modelu kolejki
      """
      from apps.enrollment.courses.models import PointsOfCourses,\
                                          PointsOfCourseEntities

      if student and (
           (student.dyskretna_l and course.dyskretna_l) or
           (student.numeryczna_l and course.numeryczna_l)
          ):
          import settings
          from apps.users.models import Program
          program = Program.objects.get(id=settings.M_PROGRAM)
                                          
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
    def is_ECTS_points_limit_exceeded(user, group):
      """
          check if the sum of ECTS points for every course student is enrolled on, exceeds limit
          TODO: OMFG, to nie powinno być w modelu kolejki
      """
      try:
            semester = Semester.get_default_semester()
            student = user.student
            """ Sprawdzenie, czy obowiązuje jeszcze limit ECTS"""
            limit_abortion_date = group.course.semester.records_ects_limit_abolition
            if limit_abortion_date and limit_abortion_date < datetime.now():
                return False
            """ Obliczenie sumy punktów ECTS"""
            groups = map(lambda x: x.group, \
                Record.objects.filter(student=student, \
                    group__course__semester__in=[semester], \
                    status=STATUS_ENROLLED).select_related(\
                    'group', 'group__course', 'group__course__entity'))
            courses = set([g.course for g in groups])
            program = user.student.program
            points = Queue.get_point(program, group.course, student)
            ects = sum([Queue.get_point(program,course, student) for course in courses])

            if group.course not in courses:
                ects += points

    	    """ Porównanie sumy z obowiązującym limitem"""
            if ects <= ECTS_LIMIT:
                return False
            else:
                return True
      except Student.DoesNotExist:
            logger.warning('Queue.count_ECTS_points(user_id)  throws Student.DoesNotExist exception (parameters: user_id = %d)' % (int(user.id)))
            raise NonStudentException()
            
    
    @staticmethod
    def remove_first_student_from_queue(group):
        '''
            return FIRST student (student's queue record) from queue whose ECTS
            points limit is not excedeed, remove this student and all students
            before him from queue
            
            ignore students, which not "zamawiany", if there is no space for
            them (but there is some for "zamawiany")
            
            returns None, when there is no space for students left at all
        '''
        if (group.get_count_of_enrolled(dont_use_cache=False) >= group.limit):
            return None
        only_zamawiany = group.available_only_for_zamawiane()
        
        queue = Queue.queued.filter(group=group).order_by('time')
        for queued in queue:
            student = queued.student
            if (only_zamawiany and not student.is_zamawiany()):
                continue
                
            Queue.remove_student_from_queue(student.user.id, group.id)
            
            # Sprawdzenie mozliwosci zapisania studenta na zajęcia
            if Queue.is_ECTS_points_limit_exceeded(student.user, group):
                # Wyrzucenie studenta z kolejki. Jego limit ECTS nie pozwala
                # zapisać go do grupy, na którą oczekuje
                logger.info('User %s <id: %s> is now removed as first from \
                    queue of group "%s" <id %s> but he exceeded ECTS limit' % \
                    (student.user.username, student.user.id, group, group.id))
                continue
            logger.info('User %s <id: %s> is now removed as first from queue \
                of group "%s" <id %s>' % \
                (student.user.username, student.user.id, group, group.id))
            return queued
        return None
    
    @staticmethod
    def try_enroll_next_student(group):

        if not group.enrollment_are_open():
            return False

        queued = Queue.remove_first_student_from_queue(group)
        if not queued:
            return False
        
        Record.add_student_to_group(queued.student.user, group)
        Queue.remove_student_low_priority_records(queued.student.user.id, \
            group.id, queued.priority)
        
        mail_enrollment_from_queue(queued.student, group)
        logger.info('User %s <id: %s> enrolled from queue in group [%s] \
            <id: %s>.', queued.student.user.username, queued.student.user.id, \
            group, group.id)
        return True
    
    @staticmethod
    def get_groups_for_student(user):
        """ Return all groups that student is trying to sign to."""
        try:
            student = user.student
            return map(lambda x: x.group, Queue.queued.filter(student=student))
        except Student.DoesNotExist:
            logger.warning('Queue.get_groups_for_student(user_id = %d) throws Student.DoesNotExist exception.' % int(user.id))
            raise NonStudentException()
    
    @staticmethod
    def remove_student_low_priority_records(user_id, group_id, priority) :
        """ Funkcja, która czyści kolejkę z wpisów do grup z tego samego przedmiotu o tym samym rodzaju ale mniejszym priorytecie"""
        user = User.objects.get(id = user_id)
        try:

            """ Pobranie listy grup z tego samego przedmiotu i tego samego typu, na które próbuje się zapisać student"""
            """ Dalej są jakieś herezje, imho powinno być:
            group = Group.objects.get(id = group_id).select_related('course')
            queued = Queue.queued.filter(student=user.student, group__course=group.course, group__type=group.type).select_related('group') #jedno zapytanie zamiast kilkudziesieciu!!!!
                for queue in queued:
                    if queue.priority <= priority:
                        logger.info('User %s <id: %s> is now removed from queue of group "%s" <id: %s> because of low priority (%s)' % (user.username, user.id, queue.group, queue.group.id, priority))
                        Queue.remove_student_from_queue(user_id,q_g.id)
            """
            student = user.student
            group = Group.objects.get(id = group_id)
            course = Course.objects.get(slug = group.course_slug())
            queued_group = [g for g in Queue.get_groups_for_student(user) if g.course == course and g.type == group.type]
            """ Usunięcie wszystkich wpisów z kolejki, które są na liście queued_group i posiadają niższy priorytet od zadanego"""
            for q_g in queued_group :
                record = Queue.queued.get(student = student,group = q_g) #WTF?!
                if (record.priority <= priority) :
                    logger.info('User %s <id: %s> is now removed from queue of group "%s" <id: %s> because of low priority (%s)' % (user.username, user.id, q_g, q_g.id, priority))
                    Queue.remove_student_from_queue(user_id,q_g.id)
        except Student.DoesNotExist:
            logger.warning('Queue.remove_student_low_priority_records throws Student.DoesNotExist exception (parameters user_id = %d, group_id = %d, priority = %d)' % (int(user_id), int(group_id), int(priority)))
            raise NonStudentException()
        except Group.DoesNotExist:
            logger.warning('Queue.remove_student_low_priority_records throws Group.DoesNotExist exception (parameters user_id = %d, group_id = %d, priority = %d)' % (int(user_id), int(group_id), int(priority)))
            raise NonGroupException()

    @staticmethod
    def queue_priorities_map(queue_set):
        raw = queue_set.values('group__id', 'priority')
        m = {}
        for r in raw:
            m[r['group__id']] = r['priority']
        return m
    
    @staticmethod
    def queue_priorities_map_values(queue_values):
        m = {}
        for r in queue_values:
            m[r['group_id']] = r['priority']
        return m

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

    group = instance


    if not group.enrollment_are_open():
        return

    if Group.disable_update_signal:
        return

    while (Queue.try_enroll_next_student(group)):
        continue

def log_add_record(sender, instance, created, **kwargs):
    if instance.status == STATUS_ENROLLED:
        backup_logger.info('[01] user <%s> is added to group <%s>' % (instance.student.user.id, instance.group.id))
        
def log_delete_record(sender, instance, **kwargs):
    if instance.status == STATUS_ENROLLED and instance.group:
        backup_logger.info('[03] user <%s> is removed from group <%s>' % (instance.student.user.id, instance.group.id))

def update_group_counts(sender, instance, **kwargs):
    try:
        instance.group.update_students_counts()
    except ObjectDoesNotExist:
        pass

signals.post_save.connect(log_add_record, sender=Record)                               
signals.pre_delete.connect(log_delete_record, sender=Record) 
signals.post_save.connect(update_group_counts, sender=Record)
signals.post_delete.connect(Record.on_student_remove_from_group, sender=Record)
signals.post_save.connect(update_group_counts, sender=Queue)
signals.post_delete.connect(update_group_counts, sender=Queue)
signals.post_save.connect(add_people_from_queue, sender=Group)
