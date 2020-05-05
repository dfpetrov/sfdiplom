# Generated by Django 3.0.3 on 2020-05-03 11:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0080_course_profit'),
    ]

    operations = [
        migrations.AddField(
            model_name='currentlesson',
            name='course',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='current_lessons', to='appcourses.Course'),
        ),
    ]