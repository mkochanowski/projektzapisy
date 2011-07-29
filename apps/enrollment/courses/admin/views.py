# -*- coding: utf-8 -*-

from traceback import format_tb
from sys import exc_info, path
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from django.http import HttpResponse
from tempfile import NamedTemporaryFile
from importschedule import import_semester_schedule
import os

FEREOL_PATH = os.getcwd()
path.append(FEREOL_PATH + '/dbimport/schedule')
from scheduleimport import scheduleimport



class SemesterImportForm(forms.Form):
    file = forms.FileField(max_length=255, label='Plik XML')

@staff_member_required
def import_semester(request):
    if request.method == 'POST':
        form = SemesterImportForm(request.POST, request.FILES)
        
        if form.is_valid():
            xmlfile = NamedTemporaryFile();
        
            for chunk in request.FILES['file'].chunks():
                xmlfile.write(chunk)
                
            xmlfile.seek(0)
            
            try:    
                import_semester_schedule(xmlfile)
    	    except Exception:
                errormsg = unicode(exc_info()[0]) + ' ' + unicode(exc_info()[1]) + '\n\n'
                errormsg += u'Traceback:\n'
                errormsg += u''.join([str for str in format_tb(exc_info()[2])])
                request.user.message_set.create(message="Błąd!")
            else:
                errormsg = None
                request.user.message_set.create(message="Plik został zaimportowany.")
            finally:    
                xmlfile.close()
        
            return render_to_response(
                'enrollment/courses/admin/import_semester.html',
                {'form': form,
                'errormsg': errormsg,
                },
                RequestContext(request, {}),
            )
    else:
        form = SemesterImportForm()

    return render_to_response(
        'enrollment/courses/admin/import_semester.html',
        {'form': form,
        },
        RequestContext(request, {}),
    )
    
    
    
class ScheduleImportForm(forms.Form):
    file = forms.FileField(max_length=255, label='Plik z planem zajęć')

@staff_member_required
def import_schedule(request):
    if request.method == 'POST':
        form = ScheduleImportForm(request.POST, request.FILES)
        
        if form.is_valid():
            schedulefile = NamedTemporaryFile();
        
            for chunk in request.FILES['file'].chunks():
                schedulefile.write(chunk)
                
            schedulefile.seek(0)
            #schedulefile = open(schedulefile)
            try:    
                scheduleimport(schedulefile)
            except Exception:
                errormsg = unicode(exc_info()[0]) + ' ' + unicode(exc_info()[1]) + '\n\n'
                errormsg += u'Traceback:\n'
                errormsg += u''.join([str for str in format_tb(exc_info()[2])])
                request.user.message_set.create(message="Błąd!")
            else:
                errormsg = None
                request.user.message_set.create(message="Plik został zaimportowany.")
            #finally:    
                #xmlfile.close()
        
            return render_to_response(
                'enrollment/courses/admin/import_schedule.html',
                {'form': form,
                'errormsg': errormsg,
                },
                RequestContext(request, {}),
            )
    else:
        form = ScheduleImportForm()

    return render_to_response(
        'enrollment/courses/admin/import_schedule.html',
        {'form': form,
        },
        RequestContext(request, {}),
    )    