# Generated by Django 3.0.3 on 2020-05-02 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0079_auto_20200502_1922'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='profit',
            field=models.TextField(default='', max_length=2000, verbose_name='Портрет выпускника'),
        ),
    ]
