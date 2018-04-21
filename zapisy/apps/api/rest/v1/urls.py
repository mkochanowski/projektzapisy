from rest_framework import routers

from .views import ClassroomViewSet, SemesterViewSet

router = routers.DefaultRouter()
router.register(r'semesters', SemesterViewSet)
router.register(r'classrooms', ClassroomViewSet)
