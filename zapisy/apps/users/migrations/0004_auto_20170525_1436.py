# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20170525_1436'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='last_news_view',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 25, 14, 36, 46, 481872)),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='student',
            name='last_news_view',
            field=models.DateTimeField(default=datetime.datetime(2017, 5, 25, 14, 36, 46, 481872)),
            preserve_default=True,
        ),
    ]
