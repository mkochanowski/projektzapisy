# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20170522_1129'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='last_news_view',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 25, 14, 36, 16, 957195)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='student',
            name='last_news_view',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 25, 14, 36, 16, 957195)),
            preserve_default=True,
        ),
    ]
