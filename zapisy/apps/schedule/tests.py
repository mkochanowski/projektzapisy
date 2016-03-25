from django.test import TestCase
from .models import SpecialReservation
from apps.enrollment.courses.models import Semester, Classroom, Term
from datetime import datetime, timedelta, time
from django.core.serializers import serialize
from django.core.validators import ValidationError


class SpecialReservationTestCase(TestCase):

    def setUp(self):
        semester = Semester(type=Semester.TYPE_SUMMER,
                            visible=True,
                            year='2016/17',
                            semester_beginning=datetime(2016, 1, 1),
                            semester_ending=datetime(2016, 6, 30))
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
        reservations = SpecialReservation.get_reservations_for_semester()
        self.assertTrue(reservations)

    def test_no_reservations_on_not_reserved_day(self):
        reservations = SpecialReservation.get_reservations_for_semester(day_of_week=Term.FRIDAY)
        self.assertFalse(reservations)

    def test_number_of_reservations(self):
        reservations = SpecialReservation.get_reservations_for_semester()
        self.assertEqual(len(reservations), 2)

    def test_try_clean_on_overlapping_reservation(self):
        semester = Semester.get_current_semester()
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
        semester = Semester.get_current_semester()
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
