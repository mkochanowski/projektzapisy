# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-07-08 23:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('theses', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='thesis',
            name='status',
            field=models.SmallIntegerField(choices=[((1,), 'poddana pod głosowanie'), ((2,), 'zwrócona do poprawek'), ((3,), 'zaakceptowana'), ((4,), 'w realizacji'), ((5,), 'obroniona')], default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='thesis',
            name='advisor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='thesis_advisor', to='users.Employee'),
        ),
        migrations.AlterField(
            model_name='thesis',
            name='auxiliary_advisor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='thesis_auxiliary_advisor', to='users.Employee'),
        ),
        migrations.AlterField(
            model_name='thesis',
            name='kind',
            field=models.SmallIntegerField(choices=[(0, 'mgr'), (1, 'inż'), (2, 'lic'), (3, 'lic+inż'), (4, 'isim')]),
        ),
        migrations.AlterField(
            model_name='thesis',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='thesis_student', to='users.Student'),
        ),
        migrations.AlterField(
            model_name='thesis',
            name='student_2',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='thesis_student_2', to='users.Student'),
        ),
        migrations.AlterField(
            model_name='thesisvotebinding',
            name='vote',
            field=models.SmallIntegerField(choices=[(1, 'brak głosu'), (2, 'odrzucona'), (3, 'zaakceptowana'), (4, 'brak użytkownika')]),
        ),
    ]