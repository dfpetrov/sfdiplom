# Generated by Django 3.0.3 on 2020-04-13 18:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0040_auto_20200413_2155'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='slug',
            field=models.SlugField(blank=True, max_length=210, null=True, unique=True),
        ),
    ]
