# Generated by Django 3.0.3 on 2020-04-08 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0011_course_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='content',
            name='slug',
            field=models.SlugField(default='', max_length=210, unique=False),
        ),
        migrations.AddField(
            model_name='module',
            name='slug',
            field=models.SlugField(default='', max_length=210, unique=False),
        ),
    ]