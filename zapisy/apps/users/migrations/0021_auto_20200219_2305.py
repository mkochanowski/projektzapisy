# Generated by Django 2.1.13 on 2020-02-19 23:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0020_auto_20200202_1753'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='employee_ptr', related_query_name='employee', to=settings.AUTH_USER_MODEL, verbose_name='Użytkownik'),
        ),
        migrations.AlterField(
            model_name='student',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_ptr', related_query_name='student', to=settings.AUTH_USER_MODEL, verbose_name='Użytkownik'),
        ),
    ]
