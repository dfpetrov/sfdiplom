# Generated by Django 3.0.3 on 2020-04-09 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0018_auto_20200409_0825'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='content',
            options={'ordering': ['order'], 'verbose_name': 'Контент', 'verbose_name_plural': 'Контент'},
        ),
        migrations.AlterModelOptions(
            name='courseskillitem',
            options={'verbose_name': 'Компетенция', 'verbose_name_plural': 'Компетенции курса'},
        ),
        migrations.AlterModelOptions(
            name='studentscoursedata',
            options={'verbose_name': 'Запись на курс', 'verbose_name_plural': 'Записи на курс'},
        ),
        migrations.AlterField(
            model_name='courseskillitem',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Название модуля'),
        ),
    ]
