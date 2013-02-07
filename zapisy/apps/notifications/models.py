# -*- coding: utf-8 -*-
from django.db import models


NOTIFICATION_TYPES = (
    ('News', [('send-news', u'Dodano nowy news'),
              ('send-dev-news', u'Dodano nowy news developerski'),
              ('send-user_change', u'Nastąpiła automatyczna zmiana Twoich danych (np. ECTSy)')
    ]),
    ('Przedmioty', [('course-new_semester', u'Pojawiły się przedmioty na przyszły semestr'),
                      ('courses-new_schedule', u'Pojawił się plan na następny semestr'),
                      ('change-group-time', u'Grupa, w kolejce do której stoisz, ma zmieniony termin'),
                      ('change-course', u'Zmiany w opisie, ectsach przedmiotów na które jesteśmy zapisani'),
                      ('change-course-q', u'Zmiany w opisie, ectsach przedmiotów do których stoimy w kolejce'),
                      ('change-course-p', u'Zmiany w opisie, ectsach przedmiotów przypiętych do prototypu'),
                      ('course-message', u'Wykładowca napisał nową wiadomość do zapisanych'),
                      ('group-message', u'Prowadzący napisał nową wiadomość do grupy'),
    ]),
    ('Zapisy', [('enrollment-t0', u'Ustalono czasu zapisów'),
                 ('enrollment-started', u'Twoje zapisy się rozpoczęły'),
                 ('enrollment-limit', u'Podniesiono limit ECTS'),
                 ('enrollment-finish', u'Pozostały 24 godziny do końca zapisów'),
                 ('enrolled', u'Nastąpiło zapisanie/przepisanie do grupy')
                 ]),
    ('Oferta', [('vote-start', u'Rozpoczęło się głosowanie'),
                 ('vote-finish', u'Zostało 24 godziny do końca głosowania'),
                 ('vote-correction', u'Rozpoczęła się korekta głosowania'),
                 ('vote-correction-finish', u'Zostało 24 godziny do końca korekty'),
                 ('vote-summary', u'Wyślij podsumowanie oddanego głosu'),
                 ('grade-start', u'Rozpoczęła się ocena'),
                 ('grade-finish', u'Pozostało 24 godzin do końca oceny'),
                 ('grade-info', u'Wyślij potwierdzenie wygenerowania kluczy')]),

    ('Wydarzenia', [('exam-info', u'Ustalono termin egzaminu lub kolokwium'),
                      ('new-event', u'Dodano nowe wydarzenie w Instytucie'),
                      ('new-cancell', u'Interesujące Cię wydarzenie zostało odwołane'),
                      ('new-finish', u'Interesujące Cię wydarzenie odbędzie się jutro'),
                      ('message-in-event', u'Organizator wydarenia napisał nową wiadomość'),
                      ('new-zosia', u'Wyślij informacje o rozpoczęciu zapisów na nową ZOSIę')
    ]),
    ('Wnioski', [('petition-accepted', u'Twój wniosek został zaakceptowany'),
                  ('petition-deny', u'Twój wniosek został odrzucony')
                 ])
)

def types_list():
    types = []

    for elem in NOTIFICATION_TYPES:
        types.extend(elem[1])

    return types


class NotificationManager(models.Manager):

    def create_and_get(self, user):
        types = types_list()

        used = self.filter(user=user).distinct().values_list('type', flat=True)

        new_objects = []

        for t in types:
            if not t[0] in used:
                new_objects.append( NotificationPreferences(user=user, type=t[0]) )

        self.bulk_create(new_objects)


        return self.filter(user=user)

class NotificationPreferences(models.Model):
    user  = models.ForeignKey('auth.User', verbose_name=u'użytkownik')
    type  = models.CharField(choices=types_list(), max_length=50, verbose_name=u'typ')
    value = models.BooleanField(default=False, verbose_name=u'wartość')

    objects = NotificationManager()

    class Meta:
        ordering = ['id']
        verbose_name = u'Ustawienie Notyfikacji'
        verbose_name_plural = u'Ustawienia Notyfikacji'


