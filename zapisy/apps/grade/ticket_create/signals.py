from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.grade.poll.models import Poll
from apps.grade.ticket_create.models import SigningKey


@receiver(post_save, sender=Poll)
def generate_key(sender: Poll, instance: Poll, **kwargs) -> None:
    if not kwargs['created']:
        # Skip if Poll is being modified rather than created.
        return
    pem_rsa_key = SigningKey.generate_rsa_key()
    key = SigningKey(poll=instance, private_key=pem_rsa_key)
    key.save()
