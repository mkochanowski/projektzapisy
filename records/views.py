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
      ex.delete()
      msg = 'Zostałeś wypisany'
    except: 
      r = Record(group = sel_group, student = my_profile)
      r.save()
      msg = 'Zostałeś zapisany'
      
    request.user.message_set.create( message = msg )
    
    return HttpResponseRedirect( '/subjects/%s' % sel_group.subject.slug )

@login_required
def own(request):

    user = request.user
    my_profile = User.objects.get(id = user.id)
    data = {'groups' : Record.objects.filter(student=my_profile)}

    return render_to_response( 'records/own.html', data)
