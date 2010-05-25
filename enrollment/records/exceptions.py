class NonStudentException(Exception):
    """is thrown when student does not exists"""
    pass

class NonGroupException(Exception):
    """is thrown when group does not exists"""
    pass

class AlreadyAssignedException(Exception):
    """is thrown when student try to join to the group which member already is"""
    pass

class AssignedInThisTypeGroupException(AlreadyAssignedException):
    """is thrown when student try to join to the group after have enrolled same to other of same type"""
    pass

class AlreadyNotAssignedException(Exception):
    """is thrown when student try to sign out from not enrolled group"""
    pass

class AlreadyPinnedException(Exception):
    """is thrown when user tries to enroll to the same group twice"""
    pass

class AlreadyNotPinnedException(Exception):
    """is thrown when user tries to sign out of the group twice in row"""
    pass

class OutOfLimitException(Exception):
    """is thrown when someone tries to join already full group"""
    pass

class RecordsNotOpenException(Exception):
    """is thrown when someone tries to enroll to subject and he do not have open enrollings for that subject at that time"""
    pass
