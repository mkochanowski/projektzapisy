# -*- coding: utf-8 -*-

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from fereol.subjects.models import *
from fereol.users.models import *
from fereol.records.models import *

def change( request, group_id):

    user = request.user
    gid = int(group_id)
 
    my_profile = User.objects.get(id = user.id)
    sel_group = Group.objects.get(id = gid)

    data = {}
 
    try:
      ex = Record.objects.get(group = sel_group, student = my_profile)
     
      ex.delete()
      data = {'message' : 'Wypisano Ciebie z grupy'}
    except: 
      r = Record(group = sel_group, student = my_profile)
      r.save()
      data = {'message' : 'Zapisano Ciebie do grupy'}
 
    return render_to_response( 'records/status.html', data)

def own(request):

    user = request.user
    my_profile = User.objects.get(id = user.id)
    data = {'groups' : Record.objects.filter(student=my_profile)}

    return render_to_response( 'records/own.html', data)
