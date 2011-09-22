# -*- coding: utf-8 -*-

from traceback import format_tb
from sys import exc_info, path
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.admin.views.decorators import staff_member_required
from django import forms
from django.http import HttpResponse
from tempfile import NamedTemporaryFile
import os
from apps.users.models import StudiaZamawiane


class ZamawianiImportForm(forms.Form):
    file = forms.FileField(max_length=255, label='Plik z danymi')

@staff_member_required
def import_zamawiani(request):
    if request.method == 'POST':
        form = ZamawianiImportForm(request.POST, request.FILES)
        
        if form.is_valid():
            zamawianifile = NamedTemporaryFile();
        
            for chunk in request.FILES['file'].chunks():
                zamawianifile.write(chunk)
                
            zamawianifile.seek(0)
            try: 
                pass
                #scheduleimport(schedulefile)
            except Exception:
                errormsg = unicode(exc_info()[0]) + ' ' + unicode(exc_info()[1]) + '\n\n'
                errormsg += u'Traceback:\n'
                errormsg += u''.join([str for str in format_tb(exc_info()[2])])
                request.user.message_set.create(message="Błąd!")
            else:
                errormsg = None
                request.user.message_set.create(message="Plik został zaimportowany.")
        
            return render_to_response(
                'users/import_zamawiani.html',
                {'form': form,
                'errormsg': errormsg,
                },
                RequestContext(request, {}),
            )
    else:
        form = ZamawianiImportForm()

    return render_to_response(
        'users/import_zamawiani.html',
        {'form': form,
        },
        RequestContext(request, {}),
    )    
    
    
@staff_member_required    
def export_zamawiani(request):
    zamawiani = StudiaZamawiane.objects.all().select_related('student','user')
    zamawiani = map(lambda x: "|".join([x.student.user.first_name, x.student.user.last_name,x.student.matricula,x.bank_account or '']), zamawiani)
    zamawiani = '\n'.join(zamawiani)
    response = HttpResponse(zamawiani, content_type='application/txt')
    response['Content-Disposition'] = 'attachment; filename=fereol_zamawiani.txt'
    return response   
    
    