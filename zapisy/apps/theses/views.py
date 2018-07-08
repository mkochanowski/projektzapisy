from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from rest_framework import permissions

from . import models
from . import serializers

class ThesesViewSet(viewsets.ModelViewSet):
    http_method_names = ["patch", "get"]
    permission_classes = (permissions.AllowAny,)
    queryset = models.Thesis.objects.all()
    serializer_class = serializers.ThesisSerializer

@login_required
def theses_main(request):
    return render(request, "theses/main.html")
