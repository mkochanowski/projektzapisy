from .models import Semester
from datetime import datetime


class SemesterObjectMother():

    @staticmethod
    def winter_semester_2015_16():
        """Records opening and closing dates are made up"""
        semester = Semester(
            visible=True,
            type=Semester.TYPE_WINTER,
            year='2015/16',
            records_opening=datetime(2015, 9, 20),
            records_closing=datetime(2015, 10, 14),
            lectures_beginning=datetime(2015, 10, 1),
            lectures_ending=datetime(2016, 2, 3),
            semester_beginning=datetime(2015, 10, 1),
            semester_ending=datetime(2016, 2, 21),
        )
        return semester

    @staticmethod
    def summer_semester_2015_16():
        """Records opening and closing dates are made up"""
        semester = Semester(
            visible=True,
            type=Semester.TYPE_SUMMER,
            year='2015/16',
            records_opening=datetime(2016, 2, 24),
            records_closing=datetime(2016, 3, 14),
            lectures_beginning=datetime(2016, 2, 22),
            lectures_ending=datetime(2016, 6, 16),
            semester_beginning=datetime(2016, 2, 22),
            semester_ending=datetime(2016, 9, 10)
        )
        return semester
