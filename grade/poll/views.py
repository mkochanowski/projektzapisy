# Create your views here.

from django.http                    import HttpResponse
from django.shortcuts               import render_to_response
from django.template                import RequestContext

def create(request):
    return render_to_response ('grade/poll/add.html', context_instance = RequestContext( request ))

def default(request):
    return render_to_response ('grade/poll/main.html', context_instance = RequestContext ( request ))
