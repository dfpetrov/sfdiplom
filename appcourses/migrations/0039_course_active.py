# Generated by Django 3.0.3 on 2020-04-13 16:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0038_questionresult'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='active',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Активен'),
        ),
    ]
