# -*- coding: utf8 -*-

from django.db import models
     
class PointTypes(models.Model):
    """types of points"""
    name = models.CharField(max_length=30, verbose_name='rodzaj punktów', default="", unique=False)

    class Meta:
        verbose_name = 'rodzaj punktu'
        verbose_name_plural = 'rodzaje punktów'
        app_label = 'courses'

    def __unicode__(self):
        return '%s' % (self.name, )

class PointsOfCourseEntities(models.Model):
    """
        Model przechowuje punkty przypisane do :model:`courses.CourseEntity` oraz :model:'courses.PointTypes'

        Pole program jest opcjonalne.

         * Zasada wyznaczenia punktów *

         Student X jest na programie Y. Sprawdzamy ile jest dla niego przedmiot Z.
         Jeżeli istnieje rekord łączący program z podstawą dostajemy wartość z niego.
         W przeciwnym wypadku zwracamy wartość z rekordu w którym program == Null, entity==Z, a typ punktów
         zgadza się z typem przypisanym do osoby.
         Jeżeli nie istnieje rekord spełniający powyższe przypadki zwracamy zero.

         * Uwaga *

         Przedmioty posiadające wersje L i M mają modyfikatory zmieniające program.

         Czytanie z tej tabeli powinno odbywać się poprzez metody z :model:`courses.CourseEntity`
         w innym wypadku ryzykujemy otrzymanie nieprawidłowej wartości.


    """
    entity = models.ForeignKey('CourseEntity', verbose_name='podstawa przedmiotu')
    type_of_point = models.ForeignKey('PointTypes', verbose_name='rodzaj punktów')
    program = models.ForeignKey('users.Program', verbose_name='Program Studiów', null=True, blank=True, default=None)
    value = models.PositiveSmallIntegerField(verbose_name='liczba punktów', default=6)

    class Meta:
        verbose_name = 'zależność podstawa przedmiotu-punkty'
        verbose_name_plural = 'zależności podstawy przedmiotu-punkty'
        app_label = 'courses'
        unique_together = ('entity', 'type_of_point', 'program')

    def __unicode__(self):
        return '%s: %s %s' % (self.entity.name, self.value, self.type_of_point)


    @classmethod
    def get_course_points(cls, course, type=None):
        """

        @param course: :model:'courses.Course'
        @param type: :model:'courses.PointTypes'
        @return :model:'courses.PointsOfCourseEntities'

        """
        return 6
#        return cls.objects.filter(entity=course.entity, type_of_point=type).order_by('-value')[0]

class Points(models.Model):
    """
    Widok materialny (patrz migracja)
    """
    value    = models.PositiveSmallIntegerField(verbose_name='liczba punktów')
    enrolled = models.BooleanField()
    course   = models.ForeignKey('courses.Course', on_delete=models.DO_NOTHING, primary_key=True)
    entity   = models.ForeignKey('CourseEntity', on_delete=models.DO_NOTHING)
    student  = models.ForeignKey('users.Student', on_delete=models.DO_NOTHING)


    class Meta:
        managed = False

    @classmethod
    def get_for_student(cls, course, student):
        """

        Return Points for student

        @param course: :model:'courses.Course'
        @param student:  :model:'users.Student'
        @return :model:'courses.Points'
        """
        return 6
#        return cls.objects.get(course=course, student=student)
