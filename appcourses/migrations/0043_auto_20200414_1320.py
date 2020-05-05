# Generated by Django 3.0.3 on 2020-04-14 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0042_auto_20200413_2217'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='active',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Активна'),
        ),
        migrations.AddField(
            model_name='lesson',
            name='type',
            field=models.CharField(choices=[('l', 'Lesson'), ('q', 'Quiz')], default='l', max_length=1, null=True, verbose_name='Тип'),
        ),
    ]