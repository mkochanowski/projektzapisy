# -*- coding: utf-8 -*-
from django.test import TestCase
from django.utils.crypto import get_random_string
from random import randint
from zapisy.apps.schedule.models import SpecialReservation, Event, Term as EventTerm
from apps.enrollment.courses.models import Semester, Classroom, Term
from datetime import datetime, timedelta, time, date
from django.core.serializers import serialize
from django.core.validators import ValidationError
from django.contrib.auth.models import User
from apps.enrollment.courses.tests.objectmothers import SemesterObjectMother, ClassroomObjectMother
from apps.users.tests.objectmothers import UserObjectMother


import zapisy.common as common
import factory

class SpecialReservationFactory(factory.django.DjangoModelFactory):
	class Meta:
		model = SpecialReservation
        
	title = get_random_string(length=randint(5,20))
	classroom=Classroom.get_by_number('104')
	dayOfWeek=common.WEDNESDAY
	start_time=time(15)
	end_time=time(randint(16,20))
	#author = factory.SubFactory(UserFactory) for semester
	semester = Semester.get_semester(date(2016, 5, 12))
 
