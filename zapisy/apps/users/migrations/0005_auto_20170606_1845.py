# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20170606_1842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='openingtimesview',
            name='student',
            field=models.OneToOneField(related_name='opening_times', primary_key=True, serialize=False, to='users.Student'),
        ),
    ]
