# Generated by Django 3.0.3 on 2020-04-11 17:57

import appcourses.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0032_auto_20200411_1930'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='order',
            field=appcourses.fields.OrderField(blank=True, default=0),
        ),
        migrations.AlterField(
            model_name='question',
            name='description',
            field=models.TextField(default='', max_length=1000, null=True, verbose_name='Примечание'),
        ),
    ]
