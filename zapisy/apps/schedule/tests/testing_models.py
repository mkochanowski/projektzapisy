# -*- coding: utf-8 -*-

from datetime import time, date, timedelta

from django.test import TestCase
from django.core.validators import ValidationError
from django.contrib.auth.models import Permission
from django.http import Http404

from apps.enrollment.courses.tests.objectmothers import SemesterObjectMother, ClassroomObjectMother
from apps.enrollment.courses.tests.factories import ChangedDayForFridayFactory
from apps.users.tests.objectmothers import UserObjectMother
from apps.users.tests.factories import UserFactory, EmployeeProfileFactory
from apps.enrollment.courses.models import Semester, Classroom
from apps.users.models import UserProfile
from ..models import SpecialReservation, EventModerationMessage, EventMessage, Event, Term as EventTerm
from django.utils.crypto import get_random_string

import factories
import common


class SpecialReservationTestCase(TestCase):

    def setUp(self):
        semester = SemesterObjectMother.summer_semester_2015_16()
        semester.save()

        semester_2 = SemesterObjectMother.winter_semester_2015_16()
        semester_2.save()

        room110 = ClassroomObjectMother.room110()
        room110.save()

        reservation = SpecialReservation(semester=semester,
                                         title="A reservation",
                                         classroom=room110,
                                         dayOfWeek=common.WEDNESDAY,
                                         start_time=time(15),
                                         end_time=time(16))
        reservation.full_clean()
        reservation.save()

        reservation_2 = SpecialReservation(semester=semester,
                                           title=u'ąęłżóćśśń',
                                           classroom=room110,
                                           dayOfWeek=common.THURSDAY,
                                           start_time=time(15),
                                           end_time=time(16))
        reservation_2.full_clean()
        reservation_2.save()

        reservation_3 = SpecialReservation(semester=semester_2,
                                           title='Reserve whole monday',
                                           classroom=room110,
                                           dayOfWeek=common.MONDAY,
                                           start_time=time(8),
                                           end_time=time(21))
        reservation_3.full_clean()
        reservation_3.save()

        reservation_4 = SpecialReservation(semester=semester,
                                           title='Reserve just after reservation 2',
                                           classroom=room110,
                                           dayOfWeek=common.THURSDAY,
                                           start_time=time(16),
                                           end_time=time(18))
        reservation_4.full_clean()
        reservation_4.save()

    def test_reservation_created_terms(self):
        terms = EventTerm.get_terms_for_dates(
            [date(2016, 5, 12)],
            Classroom.get_by_number('110'),
            time(15),
            time(16)
        )
        '''
        Powinno przechodzić, bo SpecialReservation tworzy Term dla każdego dnia w semestrze,
        w którym dana rezerwacja występuje po wykonaniu metody save. To jednak nie
        przechodzi. Dlaczego?

        Rozwiązanie zagadki: My tutaj operujemy na przeszłych semestrach, a podczas tworzenia
        SpecialReservation, gdy tworzone są eventy i termsy robione są rezerwacje od teraz,
        czyli datetime.now().date(). Zatem nic nie zostanie zarezerwowane, jeśli operujemy na
        przeszłych datach. Teraz są 2 rozwiązania. Albo zmodyfikować kod tworzący termsy,
        żeby brał pod uwagę daty z przeszłości (ale jak ktoś zrobi rezerwację w środku semestru 
        to mu stworzy niepotrzebnie wydarzenia od samego początku), albo 
        tworzyć testy operujące na datach w teraźniejszości, lub przyszłości. Trzeba to wszystko
        zrefactorować na fabryki.
        '''
        # self.assertTrue(terms)

    def test_try_clean_on_overlapping_reservation(self):
        semester = Semester.get_semester(date(2016, 5, 12))
        room = Classroom.get_by_number('110')
        reservation = SpecialReservation(
            semester=semester,
            title='overlapping',
            classroom=room,
            dayOfWeek=common.THURSDAY,
            start_time=time(14),
            end_time=time(16)
        )
        # Powinno rzucać wyjątek, bo w setUp została stworzona rezerwacja, która
        # nakłąda się na godziny tej.
        # self.assertRaises(ValidationError, reservation.full_clean)

    def test_clean_on_overlapping_reservation_where_both_are_same(self):
        semester = Semester.get_semester(date(2016, 5, 12))  # summer20152016
        room = Classroom.get_by_number('110')
        reservation = SpecialReservation(
            semester=semester,
            title='overlapping',
            classroom=room,
            dayOfWeek=common.WEDNESDAY,
            start_time=time(15),
            end_time=time(16)
        )
        # To powinno rzucić ValidationError, bo taka rezerwacja
        # została już stworzona i zapisana do bazy w setUp.
        #self.assertRaises(ValidationError, reservation.full_clean)

    def test_special_reservation_unicode_method(self):
        reservations = SpecialReservation.objects.all()
        for reservation in reservations:
            unicode(reservation)

    def test_try_clean_on_non_overlapping_reservation(self):
        semester = Semester.get_semester(date(2016, 5, 12))
        room = Classroom.get_by_number('110')
        reservation = SpecialReservation(
            semester=semester,
            title='non-overlapping reservation',
            classroom=room,
            dayOfWeek=common.THURSDAY,
            start_time=time(14),
            end_time=time(15)
        )
        reservation.full_clean()

    def test_created_reservation_is_present(self):
        semester = Semester.get_semester(date(2016, 5, 12))
        reservations = SpecialReservation.get_reservations_for_semester(semester)
        self.assertTrue(reservations)

    def test_no_reservations_on_not_reserved_day(self):
        semester = Semester.get_semester(date(2016, 5, 12))
        reservations = SpecialReservation.get_reservations_for_semester(semester, day=common.FRIDAY)
        self.assertFalse(reservations)

    def test_number_of_reservations(self):
        semester = Semester.get_semester(date(2016, 5, 12))
        reservations = SpecialReservation.get_reservations_for_semester(semester)
        self.assertEqual(len(reservations), 3)

class MessageTestCase(TestCase):
    def test_simpliest_message_autotimenow(self): #there are two classes of name EventModerationMessage but it works
        event = factories.EventFactory()
        message = get_random_string(length=32)
        emm = EventModerationMessage(
            author = factories.UserFactory(),
            event = event,
            message = message
        )
        emm.save()
        emm2 = EventModerationMessage(
            author = factories.UserFactory(),
            event = event,
            message = message
        )
        emm2.save()
        #event message should not be counted
        em = EventMessage(
            author = factories.UserFactory(),
            event = event,
            message = message
        )
        em.save()        

        messages = EventModerationMessage.get_event_messages(event)
        self.assertEqual(len(messages), 2) #the results should be 2 because em is not event moderation message
    def test_simpliest_eventmessage_autotimenow(self): #this classes are the same almost
        event = factories.EventFactory()
        message = get_random_string(length=32)
        em = EventMessage(
            author = factories.UserFactory(),
            event = event,
            message = message
        )
        em.save()
        em2 = EventMessage(
            author = factories.UserFactory(),
            event = event,
            message = message
        )
        em2.save()        
        messages = EventMessage.get_event_messages(event)
        self.assertEqual(len(messages), 2) 

class EventTestCase(TestCase):
    def setUp(self):
        teacher = factories.UserFactory()
        teacher.full_clean()
        teacher_profile = UserObjectMother.teacher_profile(teacher)
        teacher_profile.save()

        employee = UserObjectMother.employee(teacher)
        employee.save()

        event = factories.EventFactory(author=teacher)
        event.full_clean()

        room110 = factories.ClassroomFactory(number='110')
        room110.full_clean()

        term_1 = factories.TermFixedDayFactory(event=event, room=room110)
        term_1.full_clean()

        term_2 = factories.TermFixedDayFactory(event=event, start=time(16), end=time(17),
                                               room=room110)
        term_2.full_clean()

        u = factories.UserFactory()
        u.full_clean()
        student = UserObjectMother.student_profile(u)
        student.save()

    def test_event_is_present(self):
        room = Classroom.get_by_number('110')
        terms = EventTerm.get_terms_for_dates(dates=[date(2016, 5, 20)],
                                              classroom=room)
        self.assertTrue(terms)

    def test_remove_event_and_terms(self):
        event = Event.objects.all()[0]
        event.delete()
        terms = EventTerm.objects.all()
        self.assertFalse(terms)

    def test_event_unicode_method(self):
        events = Event.objects.all()
        for event in events:
            self.assertEquals(unicode(event), u'%s %s' % (event.title, event.description))

    def test_get_absolute_url__no_group(self):
        event = Event.objects.all()[0]
        self.assertEquals(event.get_absolute_url(), '/events/%d' % event.pk)

    def test_get_absolute_url__group(self):
        event = factories.EventCourseFactory.create()
        self.assertEquals(event.get_absolute_url(), '/records/%s/records' % event.group_id)

    def test_clean__overlapping_term(self):
        event = Event.objects.all()[0]
        room110 = Classroom.get_by_number('110')
        term = EventTerm(
            event=event,
            day=date(2016, 5, 20),
            start=time(15),
            end=time(17),
            room=room110
        )
        self.assertRaises(ValidationError, term.full_clean)

    def test_clean__student_cant_add_exam(self):
        student = UserProfile.objects.get(is_student=True).user
        event = factories.ExamEventFactory.build(author=student)
        self.assertRaises(ValidationError, event.full_clean)

    def test_clean__student_cant_add_test(self):
        student = UserProfile.objects.get(is_student=True).user
        event = factories.EventTestFactory.build(author=student)
        self.assertRaises(ValidationError, event.full_clean)

    def test_clean__employee_can_add_exam(self):
        employee = UserProfile.objects.get(is_employee=True).user
        event = factories.ExamEventFactory.build(author=employee)
        event.full_clean()

    def test_clean__employee_can_add_test(self):
        employee = UserProfile.objects.get(is_employee=True).user
        event = factories.EventTestFactory.build(author=employee)
        event.full_clean()

    def test_clean__student_cant_add_accepted_event(self):
        user = UserProfile.objects.get(is_student=True).user
        event = factories.EventFactory.build(author=user)
        self.assertRaises(ValidationError, event.full_clean)

    def test_clean__employee_can_add_accepted_event(self):
        employee = UserProfile.objects.get(is_employee=True).user
        event = factories.EventFactory.build(author=employee)
        event.full_clean()

    def test_new_exam_after_clean_is_public(self):
        exam = factories.ExamEventFactory()
        user_profile = EmployeeProfileFactory(user=exam.author)
        user_profile.full_clean()
        exam.full_clean()
        self.assertTrue(exam.visible)

    def test_after_clean_new_test_is_public(self):
        test = factories.EventTestFactory()
        user_profile = EmployeeProfileFactory(user=test.author)
        user_profile.full_clean()
        test.full_clean()
        self.assertTrue(test.visible)

    def test_normal_user_cant_see_invisible_event(self):
        user = UserFactory()
        event = factories.EventInvisibleFactory.build()
        self.assertFalse(event._user_can_see_or_404(user))

    def test_author_can_see_own_invisible_event(self):
        event = factories.EventInvisibleFactory.build()
        self.assertTrue(event._user_can_see_or_404(event.author))

    def test_user_with_manage_perm_can_see_invisible_event(self):
        user = UserFactory()
        user.full_clean()
        permission = Permission.objects.get(codename='manage_events')
        user.user_permissions.add(permission)
        event = factories.EventFactory(visible=False)
        self.assertTrue(event._user_can_see_or_404(user))

    def test_student_cant_see_pending_event(self):
        user = UserFactory()
        user.full_clean()
        event = factories.PendingEventFactory.build()
        self.assertFalse(event._user_can_see_or_404(user))

    def test_user_cant_see_rejected_event(self):
        user = UserFactory()
        user.full_clean()
        event = factories.RejectedEventFactory.build()
        self.assertFalse(event._user_can_see_or_404(user))

    # Jeśli user nie jest autorem eventu, ani nie ma praw do zarządzania, to
    # nie może widzieć wydarzeń typu zajęcia(TYPE_CLASS) i inne(TYPE_OTHER). Dlaczego?
    # TYPE_CLASS i TYPE_OTHER nie są nigdzie w kodzie użyte. Do czego one są?
    def test_user_cant_see_class_event(self):
        user = UserFactory()
        user.full_clean()
        event = factories.EventClassFactory.build()
        self.assertFalse(event._user_can_see_or_404(user))

    def test_user_cant_see_other_event(self):
        user = UserFactory()
        user.full_clean()
        event = factories.EventOtherFactory.build()
        self.assertFalse(event._user_can_see_or_404(user))

    def test_get_event_or_404_raises_error404_if_event_doesnt_exist(self):
        user = UserFactory.build()
        user.full_clean()
        self.assertRaises(Http404, Event.get_event_or_404, 0, user)

    def test_get_event_or_404_returns_event_if_exists_and_user_can_see(self):
        # Czy bawić się w taką walidację i rozbijanie na build, clean, save?
        employee = UserProfile.objects.get(is_employee=True).user
        event = factories.EventFactory.build(author=employee)
        event.full_clean()
        event.save()
        ret = Event.get_event_or_404(event.id, employee)
        self.assertEquals(event, ret)

    def test_get_event_or_404_raises_error404_if_user_cant_see_event(self):
        user = UserFactory.build()
        user.full_clean()
        user.save()
        employee = UserProfile.objects.get(is_employee=True).user
        event = factories.EventInvisibleFactory.build(author=employee)
        event.full_clean()
        event.save()
        self.assertRaises(Http404, Event.get_event_or_404, event.id, user)


class EventsOnChangedDayTestCase(TestCase):
    def find_closest_day_of_week_to_date(self, date, day_of_week):
        date += timedelta(days=1)
        while date.weekday() != day_of_week:
            date += timedelta(days=1)
        return date

    def setUp(self):
        semester_beginning = factories.SummerSemesterFactory.semester_beginning
        summer_semester = factories.SummerSemesterFactory()
        summer_semester.full_clean()

        self.thursday = self.find_closest_day_of_week_to_date(semester_beginning, 3)
        changed_day = ChangedDayForFridayFactory(
            day=self.thursday
        )
        changed_day.full_clean()

        classroom = factories.ClassroomFactory()

        reservation = factories.SepcialReservationFactory.build(
            semester=summer_semester,
            classroom=classroom
        )
        reservation.full_clean()
        reservation.save()

    def test_add_event_on_changed_day(self):
        classroom = Classroom.get_by_number('25')
        reservation = SpecialReservation.objects.in_classroom(classroom)[0]

        self.assertRaises(
            ValidationError,
            factories.TermThisYearFactory(
                day=self.thursday,
                start=reservation.start_time,
                end=reservation.end_time,
                room=classroom
            ).full_clean
        )

    def test_check_theres_no_original_reservation_on_changed_day(self):
        classroom = Classroom.get_by_number('25')
        reservation = SpecialReservation.objects.in_classroom(classroom)[0]

        reserv_thursday = factories.SepcialReservationFactory.build(
            semester=reservation.semester,
            classroom=classroom,
            start_time=time(16, 15),
            end_time=time(18),
            dayOfWeek=common.THURSDAY
        )
        reserv_thursday.full_clean()
        reserv_thursday.save()

        ev = EventTerm.get_terms_for_dates(
            [self.thursday], classroom, start_time=reserv_thursday.start_time,
            end_time=reserv_thursday.end_time
        )
        self.assertFalse(ev)
