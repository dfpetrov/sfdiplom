# Generated by Django 3.0.2 on 2020-01-12 09:45

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('apptasks', '0002_task_profile'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='task',
            name='profile',
        ),
        # migrations.AddField(
        #     model_name='task',
        #     name='user1',
        #     field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        # ),
    ]