# Generated by Django 3.0.3 on 2020-04-11 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0027_auto_20200411_1632'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='language',
            field=models.ManyToManyField(related_name='courses', to='appcourses.Language'),
        ),
    ]
