from django.shortcuts import render

def theses_main(request):
	return render(request, "theses/main.html")
