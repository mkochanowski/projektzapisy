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
    
    start_hour = 6
    end_hour = 20
    
    cons = { 
        'headerHeight' : 20,
        'rowHeight' : 50,
        'columnWidth' : 100,
        'tableWidth' : 100 * len(Group.DAY_OF_WEEK_CHOICES),
        'tableHeight' : 50 * (end_hour - start_hour),
    }

    try:
        student = request.user.student
    except:
        #@todo: message 'tylko studenci moga wyswietlac plan zajec'
        return HttpResponseRedirect(settings.LOGIN_URL)
    else:
        records = Record.objects.filter(student = student).order_by('group__day', 'group__start')
        groups = [record.group for record in records]
        hours = [time(x) for x in range(start_hour, end_hour+1)]
        days = Group.DAY_OF_WEEK_CHOICES
        
        for day_number, day_name in days:
            
            for hour in hours:
                
                starting_groups = [g for g in groups if g.start.hour == hour.hour and  g.day == day_number]
                num_of_intersecting = len([g for g in groups if g.start.hour <= hour.hour and  g.end.hour > hour.hour])
                num_of_starting = len(starting_groups)
                
                print starting_groups
                
                for (i, g) in zip(range(1, num_of_starting+1), starting_groups):
                   
                    g.divWidth =  cons['columnWidth']/num_of_intersecting
                    g.divLeft = (day_number) * cons['columnWidth'] + ( num_of_intersecting - num_of_starting + ( i ) ) *  g.divWidth 
                    g.divHeight = cons['rowHeight'] * (g.end.hour - g.start.hour)
                    g.divTop = cons['rowHeight'] * (hour.hour - start_hour)
        
        data = {
            'cons' : cons,
            'days': days,
            'groups': groups,
            'hours': hours,
            'records' : records,
        }
        
        return render_to_response( 'records/own.html', data, context_instance = RequestContext( request ))