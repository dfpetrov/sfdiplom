# Generated by Django 3.0.2 on 2020-01-17 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apporders', '0008_auto_20200117_1452'),
    ]

    operations = [
        migrations.AddField(
            model_name='checkpointorderitem',
            name='comment',
            field=models.TextField(default='', null=True, verbose_name='Комментарий'),
        ),
    ]
