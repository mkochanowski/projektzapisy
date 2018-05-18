from apps.users.models import Employee

class UserObjectMother:
    @staticmethod
    def employee(user):
        employee = Employee(user=user)
        employee.full_clean()
        return employee
