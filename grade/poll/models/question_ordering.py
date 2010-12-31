# -*- coding: utf8 -*-
from django.db import models

from section                   import Section
from multiple_choices_question import MultipleChoiceQuestion
from single_choice_question    import SingleChoiceQuestion
from open_question             import OpenQuestion

class OpenQuestionOrdering( models.Model ):
    question
    section
    position
    is_leading_question
    hide_on_answers
