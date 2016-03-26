from django.test import TestCase
from .models import SpecialReservation, Event, Term as EventTerm
from apps.enrollment.courses.models import Semester, Classroom, Term
from datetime import datetime, timedelta, time, date
from django.core.serializers import serialize
from django.core.validators import ValidationError
from django.contrib.auth.models import User
from apps.enrollment.courses.objectmothers import SemesterObjectMother

class SpecialReservationTestCase(TestCase):

    def setUp(self):
        semester = SemesterObjectMother.summer_semester_2015_16()
        semester.save()
        room110 = Classroom(number=110,
                            can_reserve=True)
        room110.save()
        reservation = SpecialReservation(semester=semester,
                                         title="A reservation",
                                         classroom=room110,
                                         dayOfWeek=Term.WEDNESDAY,
                                         start_time=time(15),
                                         end_time=time(16))
        reservation.save()

        reservation2 = SpecialReservation(semester=semester,
                                          title='Anoter reservation',
                                          classroom=room110,
                                          dayOfWeek=Term.THURSDAY,
                                          start_time=time(15),
                                          end_time=time(16))

        reservation2.save()

        objects = [semester, room110, reservation, reservation2]

        with open('./apps/schedule/fixtures/fixture__1.json', 'w') as out:
            serialize('json', objects, stream=out)

    def test_created_reservation_is_present(self):
        semester = Semester.get_semester(date(2016, 5, 12))
        reservations = SpecialReservation.get_reservations_for_semester(semester)
        self.assertTrue(reservations)

    def test_no_reservations_on_not_reserved_day(self):
        semester = Semester.get_semester(date(2016, 5, 12))
        reservations = SpecialReservation.get_reservations_for_semester(semester,day_of_week=Term.FRIDAY)
        self.assertFalse(reservations)

    def test_number_of_reservations(self):
        semester = Semester.get_semester(date(2016, 5, 12))
        reservations = SpecialReservation.get_reservations_for_semester(semester)
        self.assertEqual(len(reservations), 2)

    def test_try_clean_on_overlapping_reservation(self):
        semester = Semester.get_semester(date(2016, 5, 12))
        room = Classroom.get_by_number('110')
        reservation = SpecialReservation(
            semester=semester,
            title='overlapping reservation',
            classroom=room,
            dayOfWeek=Term.THURSDAY,
            start_time=time(14),
            end_time=time(17)
        )
        self.assertRaises(ValidationError, reservation.clean)

    def test_try_clean_on_non_overlapping_reservation(self):
        semester = Semester.get_semester(date(2016, 5, 12))
        room = Classroom.get_by_number('110')
        reservation = SpecialReservation(
            semester=semester,
            title='non-overlapping reservation',
            classroom=room,
            dayOfWeek=Term.THURSDAY,
            start_time=time(14),
            end_time=time(15)
        )
        reservation.clean()
