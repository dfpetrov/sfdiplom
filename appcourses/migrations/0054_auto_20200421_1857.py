# Generated by Django 3.0.3 on 2020-04-21 15:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0053_question_need_expected_result'),
    ]

    operations = [
        migrations.AddField(
            model_name='quiz',
            name='overview',
            field=models.CharField(default='', max_length=200, verbose_name='Полное описание теста'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='description',
            field=models.TextField(default='', max_length=2000, verbose_name='Краткое описание теста'),
        ),
    ]
