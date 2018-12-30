from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django_rq import job

from apps.notifications2.repositories import get_notifications_repository
from apps.notifications2.utils import render_description


@job('dispatch-notifications')
def dispatch_notifications_task(user):
    """
    Dispatch all pending notifications for the given user.
    It's purposedly designed around processing all notification_s_
    at a time instead of handling them one by one
    so we can introduce a rate-limit and/or batch them together
    should there ever be a need to do so.

    TODO: respect user's preferences
    """

    repo = get_notifications_repository()
    pending_notifications = repo.get_unsent_for_user(user)

    for pn in pending_notifications:
        ctx = {
            'content': render_description(
                pn.description_id, pn.description_args),
            'greeting': f'Dzień dobry, {user.first_name}',
        }

        send_mail(
            'Wiadomość od Systemu Zapisów IIUWr',  # FIXME (?)
            render_to_string('notifications2/email_base.html', ctx),
            settings.MASS_MAIL_FROM,
            [user.email])

        repo.mark_as_sent(user, pn)
