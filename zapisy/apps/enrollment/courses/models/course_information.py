"""Defines Courses models.

The entire course information is modeled by the CourseInformation class fields.
CourseInformation is a base class instantiated in Proposal (an abstract
Course entity spanning the years) and CourseInstance (Course being given in a
single semester).
"""

import choicesenum
from django.db import models
from django.template.defaultfilters import slugify

from apps.users.models import Employee

from .course_type import Type as CourseType
from .effects import Effects
from .tag import Tag
from .course import CourseEntity


class Language(choicesenum.ChoicesEnum):
    ENGLISH = 'en', "angielski"
    POLISH = 'pl', "polski"


class CourseInformation(models.Model):
    """CourseInformation is a class defining a Course entirely.

    It is intended to be subclassed by Proposal (in the `offer/proposal` app)
    and Course (in this app).
    """

    name = models.CharField("nazwa przedmiotu", max_length=100)
    name_en = models.CharField("nazwa po angielsku", max_length=100, blank=True)
    short_name = models.CharField("skrócona nazwa przedmiotu", max_length=30, blank=True)
    slug = models.SlugField("identyfikator URL", unique=True, max_length=255)
    description = models.TextField("opis przedmiotu", blank=True)
    language = models.CharField(
        "język wykładowy", choices=Language.choices(), max_length=2, default=Language.POLISH)
    course_type = models.ForeignKey(CourseType, verbose_name="rodzaj", on_delete=models.PROTECT)
    owner = models.ForeignKey(Employee, on_delete=models.PROTECT)
    recommended_for_first_year = models.BooleanField(
        "przedmiot polecany dla pierwszego roku", default=False)

    has_exam = models.BooleanField("przedmiot z egzaminem", default=True)

    hours_lecture = models.PositiveSmallIntegerField("godzin wykładu")
    hours_exercise = models.PositiveSmallIntegerField("godzin ćwiczeń")
    hours_lab = models.PositiveSmallIntegerField("godzin pracowni")
    hours_exercise_lab = models.PositiveSmallIntegerField("godzin ćwiczenio-pracowni")
    hours_seminar = models.PositiveSmallIntegerField("godzin seminarium")
    hours_recap = models.PositiveSmallIntegerField("godzin repetytorium")

    # Fields for syllabus
    teaching_methods = models.TextField("metody kształcenia", blank=True)
    preconditions = models.TextField("wymagania wstępne", blank=True)
    objectives = models.TextField("cele przedmiotu", blank=True)
    contents = models.TextField("treści programowe", blank=True)
    teaching_effects = models.TextField("zakładane efekty kształcenia", blank=True)
    literature = models.TextField("literatura obowiązkowa i zalecana", blank=True)
    verification_methods = models.TextField(
        "metody weryfikacji zakładanych efektów kształcenia", blank=True)
    passing_means = models.TextField("Warunki i forma zaliczenia", blank=True)
    student_labour = models.TextField("nakład pracy studenta", blank=True)

    # These fields should remain hidden from all users and are only to fill by
    # the head of teaching. Their are required for the syllabus.
    teaching_unit = models.CharField("jednostka prowadząca przedmiot", max_length=100, blank=True)
    usos_kod = models.CharField("kod przedmiotu w USOS", max_length=20, blank=True, editable=False)
    major = models.CharField("kierunek studiów", max_length=100, blank=True)
    level = models.CharField("poziom studiów", max_length=100, blank=True)
    year = models.CharField("rok studiów", max_length=50, blank=True)

    tags = models.ManyToManyField(Tag, verbose_name="tagi", blank=True)
    effects = models.ManyToManyField(Effects, verbose_name="grupy efektów kształcenia", blank=True)

    created = models.DateTimeField("Data utworzenia", auto_now_add=True)
    modified = models.DateTimeField("Data modyfikacji", auto_now=True)

    entity = models.OneToOneField(
        CourseEntity,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="tymczasowe pole ułatwiające migrację")

    def save(self, *args, **kwargs):
        """Overrides standard Django `save` function."""
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = slugify(f'{self.pk} {self.name}')
            self.save()

    def __str__(self):
        return self.name

    def __copy__(self) -> 'CourseInformation':
        """Returns a (shallow) copy of the CourseInformation object.

        All fields will be copied with exception of 'slug', 'usos_kod',
        'entity'. Names will be prepended with an indicator that the object is a
        clone.

        The returned object is not saved in the database.

        To use it run copy.copy on a model instance.
        """
        copy = CourseInformation.__new__(CourseInformation)

        # Copies all shallow fields from self to copy.
        copy.__dict__.update(self.__dict__)

        # This causes that when copy is saved, it becomes a new record.
        copy.pk = None

        # Clear some fields.
        copy.slug = None
        copy.usos_kod = None
        copy.entity = None

        return copy
