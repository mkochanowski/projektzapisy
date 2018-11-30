from django.shortcuts import render

from apps.notifications2.repositories import get_notifications_repository

def index(request):

    repo = get_notifications_repository()
    notfications = repo.get_all_for_user(request.user)

    return render(request, 'notifications2/index.html', {'notifications': notfications})
