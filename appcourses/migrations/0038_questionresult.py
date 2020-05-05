# Generated by Django 3.0.3 on 2020-04-12 13:06

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appcourses', '0037_quiz_avatar'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.TextField(default='', max_length=2000, null=True, verbose_name='Ответ пользователя')),
                ('score', models.IntegerField(blank=True, default=0, null=True, verbose_name='Баллы')),
                ('correct', models.BooleanField(blank=True, default=False, null=True, verbose_name='Ответ правильный')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('question', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_question_results', to='appcourses.Question')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_question_results', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Ответ пользователя',
                'verbose_name_plural': 'Ответы на тесты',
            },
        ),
    ]
