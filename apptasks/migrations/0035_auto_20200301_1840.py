# Generated by Django 3.0.3 on 2020-03-01 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apptasks', '0034_auto_20200301_1712'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='description',
            field=models.TextField(max_length=5000, verbose_name='Описание задачи'),
        ),
        migrations.AlterField(
            model_name='task',
            name='description_short',
            field=models.CharField(default='', max_length=120, verbose_name='Краткое описание'),
        ),
    ]
