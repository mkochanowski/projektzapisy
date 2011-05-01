# -*- coding: utf-8 -*-

"""
    News views
"""

from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect 
from django.shortcuts import render_to_response

def main_page( request ):
    return render_to_response('help/base.html', {}, context_instance = RequestContext(request))

def rules( request ):
    return render_to_response('help/rules.html', {}, context_instance = RequestContext(request))

def enrollment( request ):
    return render_to_response('help/enrollment.html', {}, context_instance = RequestContext(request))

def grade( request ):
    return render_to_response('help/grade.html', {}, context_instance = RequestContext(request))

def mobile( request ):
    return render_to_response('help/mobile.html', {}, context_instance = RequestContext(request))

def export( request ):
    return render_to_response('help/export.html', {}, context_instance = RequestContext(request))

def admin( request ):
    return render_to_response('help/admin.html', {}, context_instance = RequestContext(request))

