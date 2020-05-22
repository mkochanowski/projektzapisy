import time
import smtplib
import logging
from .lockfile import FileLock, AlreadyLocked, LockTimeout
from socket import error as socket_error

from mailer.models import Message, DontSendEntry, MessageLog

from django.conf import settings
from django.core.mail import send_mail as core_send_mail
from django.core.mail import EmailMultiAlternatives
from django.core import mail

logger = logging.getLogger('mailer.engine')

# when queue is empty, how long to wait (in seconds) before checking again
EMPTY_QUEUE_SLEEP = getattr(settings, "MAILER_EMPTY_QUEUE_SLEEP", 30)

# lock timeout value. how long to wait for the lock to become available.
# default behavior is to never wait for the lock to be available.
LOCK_WAIT_TIMEOUT = getattr(settings, "MAILER_LOCK_WAIT_TIMEOUT", -1)

EMAIL_SUBJECT_TEMPLATE = getattr(settings, "EMAIL_SUBJECT_TEMPLATE", "[ZAPISY] %s")


def prioritize():
    """
    Yield the messages in the queue in the order they should be sent.
    """

    while True:
        while Message.objects.high_priority().count() or Message.objects.medium_priority().count():
            while Message.objects.high_priority().count():
                for message in Message.objects.high_priority().order_by('when_added'):
                    yield message
            while Message.objects.high_priority().count() == 0 and Message.objects.medium_priority().count():
                yield Message.objects.medium_priority().order_by('when_added')[0]
        while Message.objects.high_priority().count() == 0 and Message.objects.medium_priority(
        ).count() == 0 and Message.objects.low_priority().count():
            yield Message.objects.low_priority().order_by('when_added')[0]
        if Message.objects.non_deferred().count() == 0:
            break


def send_all():
    """
    Send all eligible messages in the queue.
    """

    lock = FileLock("send_mail")

    logger.debug("acquiring lock...")
    try:
        lock.acquire(LOCK_WAIT_TIMEOUT)
    except AlreadyLocked:
        logger.debug("lock already in place. quitting.")
        return
    except LockTimeout:
        logger.debug("waiting for the lock timed out. quitting.")
        return
    logger.debug("acquired.")

    start_time = time.time()

    dont_send = 0
    deferred = 0
    sent = 0

    try:
        connection = mail.get_connection()
        connection.open()
        for message in prioritize():
            subject = EMAIL_SUBJECT_TEMPLATE % message.subject
            if DontSendEntry.objects.has_address(message.to_address):
                logger.info("skipping email to %s as on don't send list " % message.to_address)
                MessageLog.objects.log(message, 2)  # @@@ avoid using literal result code
                message.delete()
                dont_send += 1
            else:
                try:
                    logger.info("sending message '%s' to %s" % (subject, message.to_address))
                    if not message.message_body_html:
                        core_send_mail(
                            subject, message.message_body, message.from_address, [
                                message.to_address], connection=connection)
                    else:
                        email = EmailMultiAlternatives(
                            subject, message.message_body, message.from_address, [
                                message.to_address], connection=connection)
                        email.attach_alternative(message.message_body_html, "text/html")
                        email.send()
                    MessageLog.objects.log(message, 1)  # @@@ avoid using literal result code
                    message.delete()
                    sent += 1
                except (socket_error, smtplib.SMTPSenderRefused, smtplib.SMTPRecipientsRefused,
                        smtplib.SMTPAuthenticationError) as err:
                    message.defer()
                    logger.info("message deferred due to failure: %s" % err)
                    # @@@ avoid using literal result code
                    MessageLog.objects.log(message, 3, log_message=str(err))
                    deferred += 1
        connection.close()
    finally:
        logger.debug("releasing lock...")
        lock.release()
        logger.debug("released.")

    logger.info("")
    logger.info("%s sent; %s deferred; %s don't send" % (sent, deferred, dont_send))
    logger.info("done in %.2f seconds" % (time.time() - start_time))


def send_loop():
    """
    Loop indefinitely, checking queue at intervals of EMPTY_QUEUE_SLEEP and
    sending messages if any are on queue.
    """

    while True:
        while not Message.objects.all():
            logger.debug("sleeping for %s seconds before checking queue again" % EMPTY_QUEUE_SLEEP)
            time.sleep(EMPTY_QUEUE_SLEEP)
        send_all()
