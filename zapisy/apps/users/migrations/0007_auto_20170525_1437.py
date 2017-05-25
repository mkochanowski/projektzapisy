# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20170525_1437'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='last_news_view',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 25, 14, 37, 27, 848467)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='student',
            name='last_news_view',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 25, 14, 37, 27, 848467)),
            preserve_default=True,
        ),
    ]
