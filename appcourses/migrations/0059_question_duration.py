# Generated by Django 3.0.3 on 2020-04-23 11:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0058_quizresult_question'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='duration',
            field=models.SmallIntegerField(default=0, null=True, verbose_name='Время'),
        ),
    ]
