from apps.notifications2.repositories import get_current_repository_implementation

def notification_ico(request):
    repo = get_current_repository_implementation()
    return {"notification_counter": repo.get_count_for_user(request.user)}
