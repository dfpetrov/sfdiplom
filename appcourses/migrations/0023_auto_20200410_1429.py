# Generated by Django 3.0.3 on 2020-04-10 11:29

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appcourses', '0022_auto_20200409_1958'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='StudentsCourseData',
            new_name='CourseEnroll',
        ),
    ]