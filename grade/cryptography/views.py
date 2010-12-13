# -*- coding: utf-8 -*-
################################################################################
##          TODO:                                                             ##
##                          Dodać stan oceny (otwarta/zamknięta).             ##
##                          To będzie dodatkowe pole w modelu semestru        ##
################################################################################

from django.http                       import HttpResponse
from django.shortcuts                  import render_to_response
from django.template                   import RequestContext

from fereol.users.decorators           import student_required, employee_required
from fereol.grade.cryptography.utils   import start_the_grading_protocol
from fereol.enrollment.subjects.models import Semester

def enable_grade( request ):
    ############################################################################
    ##      TODO:                                                             ##
    ##              USTAWIĆ STATUS OCENY NA AKTYWNY                           ##
    ############################################################################
    start_the_grading_protocol(Semester.objects.all()[1]) #do poprawki - pobieranie semestru jest ała
    return render_to_response ('grade/poll/main.html', { 'message' : "Otwarto ocenę zajęć" }, context_instance = RequestContext ( request ))

def disable_grade( request ):
    ############################################################################
    ##      TODO:                                                             ##
    ##              USTWIĆ STATUS OCENY NA NIEAKTYWNY                         ##
    ############################################################################
    return render_to_response ('grade/poll/main.html', { 'message' : "Zamknięto ocenę zajęć" }, context_instance = RequestContext ( request ))
