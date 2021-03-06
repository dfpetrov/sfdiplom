# Generated by Django 3.0.3 on 2020-04-14 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0045_auto_20200414_2142'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='active',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Активна'),
        ),
        migrations.AddField(
            model_name='image',
            name='active',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Активна'),
        ),
        migrations.AddField(
            model_name='text',
            name='active',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Активна'),
        ),
        migrations.AddField(
            model_name='video',
            name='active',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Активна'),
        ),
    ]
