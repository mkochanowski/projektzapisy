from modeltranslation.translator import translator, TranslationOptions
from apps.enrollment.courses.models import CourseEntity, CourseDescription

class CourseEntityTranslationOptions(TranslationOptions):
	fields = ('name', )

translator.register(CourseEntity, CourseEntityTranslationOptions)


class CourseDescriptionTranslationOptions(TranslationOptions):
	fields = ('description',)

translator.register(CourseDescription, CourseDescriptionTranslationOptions)
