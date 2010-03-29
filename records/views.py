# -*- coding: utf-8 -*-

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from fereol.subjects.models import *
from fereol.users.models import *
from fereol.records.models import *

@login_required
    
def change( request, group_id ):

    user = request.user
    gid = int(group_id)
 
    
    my_profile = User.objects.get(id = user.id)
    sel_group = Group.objects.get(id = gid)

    msg = ''
    data = {}
 
    try:
      ex = Record.objects.get(group = sel_group, student = my_profile)    

    except: 
      r = Record(group = sel_group, student = my_profile)
  
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

    user = request.user
    my_profile = User.objects.get(id = user.id)
    data = {'groups' : Record.objects.filter(student=my_profile)}

    return render_to_response( 'records/own.html', data)
