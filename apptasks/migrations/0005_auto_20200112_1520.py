# Generated by Django 3.0.2 on 2020-01-12 12:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('apptasks', '0004_auto_20200112_1309'),
    ]

    operations = [
        # migrations.AddField(
        #     model_name='task',
        #     name='user1',
        #     field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user1', to=settings.AUTH_USER_MODEL),
        # ),
        # migrations.AlterField(
        #     model_name='task',
        #     name='author',
        #     field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='author', to=settings.AUTH_USER_MODEL),
        # ),
        migrations.AddField(
            model_name='task',
            name='author',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='author', to=settings.AUTH_USER_MODEL),
        ),
    ]
