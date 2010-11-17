# -*- coding: utf-8 -*-
"""
    Forms used to grade courses
"""
from django                   import forms
from django.utils.safestring  import SafeUnicode

from grade.poll.models        import Poll, \
                                     Answer, \
                                     OpenQuestion, \
                                     SingleChoiceQuestion, \
                                     MultipleChoiceQuestion

class KeysForm( forms.Form ):
    keysfield = forms.CharField( widget    = forms.Textarea(), 
                                 label     = "Podaj wygenerowane klucze",
                                 help_text = "Wklej tutaj pobrane wcześniej klucze." )
