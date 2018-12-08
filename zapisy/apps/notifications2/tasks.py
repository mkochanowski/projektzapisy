from django_rq import job


@job('dispatch-notifications')
def dispatch_notifications_task(user):
    print(f'SENDING FOR USER {user.id}')
