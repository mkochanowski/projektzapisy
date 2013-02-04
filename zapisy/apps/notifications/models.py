# -*- coding: utf-8 -*-
from django.db import models


NOTIFICATION_TYPES = (
    ('News', [('send-news', u'Wyślij aktualności'),
              ('send-dev-news', u'Wyślij informacje o nowościach w systemie')]),
    ('Przedmioty', ['']),
    ('Zapisy', []),
    ('Oferta', []),
    ('Wydarzenia', [('exam-info', u'Wyślij informacje o ustaleniu terminów egzaminów i kolokwiów'),
                      ('new-event', u'Wyślij informacje o nowym wydarzeniu w Instytucie'),
                      ('message-in-event', u'Wyśij wiadomość organizatora wydarzenia')])
)


class NotificationPreferences(models.Model):
    user  = models.ForeignKey('auth.User', verbose_name=u'użytkownik')
    type  = models.ForeignKey(NotificationTypes, verbose_name=u'typ')
    value = models.BooleanField(default=False, verbose_name=u'wartość')

    class Meta:
        ordering = ['type']
        verbose_name = u''