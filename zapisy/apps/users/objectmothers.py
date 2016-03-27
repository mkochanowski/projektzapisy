from .models import User, UserProfile, ExtendedUser, Student, Employee


class UserObjectMother():

    @staticmethod
    def user_jan_kowalski():
        user = User(first_name="Jan",
                    last_name="Kowalski",
                    is_staff=False,
                    is_superuser=False)
        return user

    @staticmethod
    def student_profile(user):
        profile = UserProfile(user=user,
                              is_student=True)
        return profile

    @staticmethod
    def teacher_profile(user):
        profile = UserProfile(user=user,
                              is_employee=True)
        return profile

    @staticmethod
    def employee(user):
        employee = Employee(user=user)
        return employee
