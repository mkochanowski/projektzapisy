# Generated by Django 2.1.15 on 2019-12-17 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0008_auto_20191119_0017'),
    ]

    operations = [
        migrations.AddField(
            model_name='term',
            name='ignore_conflicts',
            field=models.BooleanField(default=False),
        ),
    ]
