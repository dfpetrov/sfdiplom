# Generated by Django 3.0.3 on 2020-04-11 16:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0029_auto_20200411_1753'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='active',
            field=models.BooleanField(blank=True, null=True, verbose_name='Активен'),
        ),
        migrations.AddField(
            model_name='quiz',
            name='active',
            field=models.BooleanField(blank=True, null=True, verbose_name='Активен'),
        ),
    ]
