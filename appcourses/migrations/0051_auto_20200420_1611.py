# Generated by Django 3.0.3 on 2020-04-20 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0050_auto_20200420_1420'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='quiz',
            name='language',
        ),
        migrations.AddField(
            model_name='quiz',
            name='language',
            field=models.ManyToManyField(related_name='quizzes', to='appcourses.Language'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='type',
            field=models.CharField(choices=[('c', 'Common'), ('e', 'Exam'), ('l', 'Lesson')], default='c', max_length=1, null=True, verbose_name='Тип теста'),
        ),
    ]