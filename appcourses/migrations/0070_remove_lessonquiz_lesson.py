# Generated by Django 3.0.3 on 2020-04-28 12:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0069_lessonquiz'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lessonquiz',
            name='lesson',
        ),
    ]
