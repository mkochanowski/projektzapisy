# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext

def main_page( request ):
    """
        Main page
    """
    return render_to_response('mobile/index_m.html', context_instance = RequestContext(request))
