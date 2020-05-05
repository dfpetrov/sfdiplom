# Generated by Django 3.0.3 on 2020-04-20 10:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0048_auto_20200420_1253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='type',
            field=models.CharField(choices=[('c', 'Common'), ('e', 'Exam'), ('e', 'Lesson')], default='c', max_length=1, null=True, verbose_name='Тип теста'),
        ),
    ]
