# Generated by Django 3.0.3 on 2020-04-24 07:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0063_auto_20200424_1001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='question',
            name='duration',
            field=models.SmallIntegerField(default=0, null=True, verbose_name='Время на вопрос в секундах'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='duration',
            field=models.SmallIntegerField(default=0, null=True, verbose_name='Время на тест в секундах'),
        ),
    ]
