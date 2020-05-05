# Generated by Django 3.0.3 on 2020-04-10 11:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appcourses', '0023_auto_20200410_1429'),
    ]

    operations = [
        migrations.CreateModel(
            name='CompletedLesson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('completed', models.DateTimeField(auto_now_add=True)),
                ('lesson', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='completed_lessons', to='appcourses.Lesson')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='completed_lessons', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Завершенный урок',
                'verbose_name_plural': 'Завершенные уроки',
            },
        ),
    ]