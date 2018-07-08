from enum import Enum

"""
This helps with defining value-restricted model fields (using choices=)
"""
class ChoiceEnum(Enum):
    @classmethod
    def choices(cls):
        return tuple((opt.name, opt.value) for opt in cls)


MONDAY = '1'
TUESDAY = '2'
WEDNESDAY = '3'
THURSDAY = '4'
FRIDAY = '5'
SATURDAY = '6'
SUNDAY = '7'

DAYS_OF_WEEK = [(MONDAY, 'poniedziałek'),
                (TUESDAY, 'wtorek'),
                (WEDNESDAY, 'środa'),
                (THURSDAY, 'czwartek'),
                (FRIDAY, 'piątek'),
                (SATURDAY, 'sobota'),
                (SUNDAY, 'niedziela')]
