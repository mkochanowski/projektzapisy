# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_auto_20171112_2306'),
    ]

    operations = [
        migrations.AlterField(
            model_name='classroom',
            name='type',
            field=models.IntegerField(default=1, verbose_name=b'typ', choices=[(0, 'Sala wyk\u0142adowa'), (1, 'Sala \u0107wiczeniowa'), (2, 'Pracownia komputerowa - Windows'), (3, 'Pracownia komputerowa - Linux'), (4, 'Pracownia dwusystemowa (Windows+Linux)'), (5, 'Poligon (109)')]),
        ),
    ]
