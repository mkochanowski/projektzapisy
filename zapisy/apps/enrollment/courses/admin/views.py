# -*- coding: utf-8 -*-
import datetime
import json

from traceback import format_tb
from sys import exc_info, path
import codecs
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from django.http import HttpResponse, Http404
from tempfile import NamedTemporaryFile
from django.template.response import TemplateResponse
from django.utils.encoding import smart_unicode
from apps.enrollment.courses.models import Course, Semester, Group, Classroom
from apps.enrollment.courses.models.term import Term
from importschedule import import_semester_schedule
from apps.enrollment.courses.forms import Parser
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
                messages.error(request, u"Błąd!")
            else:
                errormsg = None
                messages.success(request, u"Plik został zaimportowany.")
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
    form = ScheduleImportForm(request.POST or None, request.FILES or None)

    if form.is_valid():

        result = Parser(request.FILES['file']).get_result()
        semester = Semester.objects.get_next()
        to_print = []
        for item in result:
            try:
                item['course'] = Course.objects.get(entity__name__iexact=item['name'], semester=semester).id
            except ObjectDoesNotExist:
                item['course'] = ''

            to_print.append(json.dumps(item))


        return TemplateResponse(request, 'enrollment/courses/admin/import_schedule_step2.html', locals())

    return TemplateResponse(request, 'enrollment/courses/admin/import_schedule.html', locals())


@staff_member_required
def finish_import_schedule(request):
    courses = request.POST.getlist('courses')
    semester = Semester.objects.get_next()
    for course in courses:
        obj = smart_unicode(course)
        c = Course.objects.get(id=course.course)

        for g in obj.groups:
            gr = Group()
            gr.course = c
            gr.teacher_id = g.teacher
            gr.type = g.type
            gr.limit = 0
            gr.save()

            t = Term()
            t.dayOfWeek = g.day
            t.start_time = datetime.time(int(g.start), 0)
            t.end_time = datetime.time(int(g.end), 0)
            t.group = gr
            t.save()

            for r in g.rooms:
                try:
                    t.classrooms.add( Classroom.objects.get(number=r) )
                except:
                    pass


    return TemplateResponse(request, 'enrollment/courses/admin/import_schedule.html', locals())