from django.shortcuts import render


def index(request):
    return render(request, 'notifications2/index.html')
