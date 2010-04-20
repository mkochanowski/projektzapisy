from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.http import HttpResponseRedirect
from django.template import RequestContext

@login_required
def profile(request):
    return redirect('/records/schedule', context_instance = RequestContext( request ))

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/')
