# Generated by Django 3.0.2 on 2020-02-13 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apptasks', '0025_auto_20200208_1814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(max_length=1500, verbose_name='Описание задачи'),
        ),
    ]
