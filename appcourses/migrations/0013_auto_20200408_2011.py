# Generated by Django 3.0.3 on 2020-04-08 17:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0012_auto_20200408_2011'),
    ]

    operations = [
        migrations.AlterField(
            model_name='content',
            name='slug',
            field=models.SlugField(default='', max_length=210),
        ),
        migrations.AlterField(
            model_name='module',
            name='slug',
            field=models.SlugField(default='', max_length=210),
        ),
    ]