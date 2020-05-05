# Generated by Django 3.0.3 on 2020-05-05 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0082_auto_20200504_1640'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='question',
            options={'ordering': ['order'], 'verbose_name': 'Вопрос', 'verbose_name_plural': 'Вопросы'},
        ),
        migrations.AlterModelOptions(
            name='quiz',
            options={'ordering': ['-created'], 'verbose_name': 'Тест', 'verbose_name_plural': 'Тесты'},
        ),
        migrations.AddField(
            model_name='course',
            name='new',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Новый'),
        ),
    ]
