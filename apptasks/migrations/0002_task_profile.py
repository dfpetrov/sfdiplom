# Generated by Django 3.0.2 on 2020-01-12 09:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appaccounts', '0002_auto_20200109_1406'),
        ('apptasks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='profile',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='appaccounts.Profile'),
        ),
    ]