# Generated by Django 3.0.2 on 2020-03-05 13:44

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appcourses', '0002_course_students'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='course',
            options={'ordering': ['-created'], 'verbose_name': 'Курс', 'verbose_name_plural': 'Курсы'},
        ),
        migrations.AlterModelOptions(
            name='module',
            options={'ordering': ['order'], 'verbose_name': 'Модуль', 'verbose_name_plural': 'Модули'},
        ),
        migrations.AlterModelOptions(
            name='subject',
            options={'ordering': ['title'], 'verbose_name': 'Раздел', 'verbose_name_plural': 'Разделы'},
        ),
        migrations.AlterField(
            model_name='course',
            name='overview',
            field=models.TextField(verbose_name='Описание'),
        ),
        migrations.AlterField(
            model_name='course',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='course_owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='course',
            name='slug',
            field=models.SlugField(max_length=210, unique=True),
        ),
        migrations.AlterField(
            model_name='course',
            name='subject',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='course_subject', to='appcourses.Subject'),
        ),
        migrations.AlterField(
            model_name='course',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Название курса'),
        ),
        migrations.AlterField(
            model_name='module',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='module_course', to='appcourses.Course'),
        ),
        migrations.AlterField(
            model_name='module',
            name='description',
            field=models.TextField(blank=True, verbose_name='Описание модуля'),
        ),
        migrations.AlterField(
            model_name='module',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Название модуля'),
        ),
        migrations.AlterField(
            model_name='subject',
            name='slug',
            field=models.SlugField(max_length=210, unique=True),
        ),
    ]