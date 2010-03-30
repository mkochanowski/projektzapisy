# -*- coding: utf-8 -*-

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from fereol.subjects.models import *
from fereol.users.models import *
from fereol.records.models import *

from datetime import time

@login_required
def change( request, group_id ):
    gid = int(group_id)
 
    try:
        student = request.user.student
    except:
        #@todo: tylko studenci mogę się zapisywac
        pass
    else:   
        try:
            sel_group = Group.objects.get(id = gid)
        except Group.DoesNotExist:
            #@todo: co jak nie istnieje grupa?
            pass
        else:
            msg = ''
            data = {}
         
            try:
                ex = Record.objects.get(group = sel_group, student = student)    
            except: 
                r = Record(group = sel_group, student = student)
                group_limit = sel_group.get_group_limit()
                students_in_group = Record.number_of_students(group = sel_group) #Record.objects.filter(group = sel_group).count()
                
                if(students_in_group < group_limit  ):
                    r.save()
                    msg = 'Zostałeś zapisany'
                else:
                    msg = 'Limit miejsc został wyczerpany, nie zostałeś zapisany'
            else:
                ex.delete()
                msg = 'Zostałeś wypisany'
                
            request.user.message_set.create( message = msg )
            
            return HttpResponseRedirect( '/subjects/%s' % sel_group.subject.slug )

@login_required
def own(request):
    
    try:
        student = request.user.student
    except:
        #@todo: message 'tylko studenci moga wyswietlac plan zajec'
        return HttpResponseRedirect(settings.LOGIN_URL)
    else:
        records = Record.objects.filter(student = student)
        groups = [record.group for record in records]
        #hours = [time(x) for x in range(start_hour, end_hour+1)]
        hours = HOURS
        #days = Group.DAY_OF_WEEK_CHOICES
        days = DAYS_OF_WEEK
        
        for group in groups:
            group.terms_ = group.get_all_terms()
            for term in group.terms_:
                #print int(term.hourTo) - int(term.hourFrom)
                term.length = (int(term.hourTo) - int(term.hourFrom))*32-4
        
        data = {
            'days': days,
            'groups': groups,
            'hours': hours,
            'records' : records,
        }
        
        return render_to_response( 'records/own.html', data, context_instance = RequestContext( request ))
    
    
    
    