# Generated by Django 2.1.14 on 2019-11-19 00:17

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedule', '0007_auto_20190528_0101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialreservation',
            name='classroom',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.Classroom', verbose_name='sala'),
        ),
        migrations.AlterField(
            model_name='specialreservation',
            name='semester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.Semester', verbose_name='semestr'),
        ),
        migrations.AlterField(
            model_name='specialreservation',
            name='title',
            field=models.CharField(max_length=255, verbose_name='nazwa'),
        ),
    ]
