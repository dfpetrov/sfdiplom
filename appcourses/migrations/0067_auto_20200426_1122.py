# Generated by Django 3.0.3 on 2020-04-26 08:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0066_auto_20200424_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionresult',
            name='answer_code',
            field=models.TextField(default='', max_length=2000, null=True, verbose_name='Код ответ пользователя'),
        ),
        migrations.AlterField(
            model_name='questionresult',
            name='answer',
            field=models.TextField(default='', max_length=2000, null=True, verbose_name='Ответ пользователя JSON'),
        ),
    ]
