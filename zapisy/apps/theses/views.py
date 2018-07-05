from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def theses_main(request):
	return render(request, "theses/main.html")
