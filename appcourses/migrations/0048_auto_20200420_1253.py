# Generated by Django 3.0.3 on 2020-04-20 09:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appcourses', '0047_auto_20200415_2128'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='courseenroll',
            options={'ordering': ['-enrolled'], 'verbose_name': 'Запись на курс', 'verbose_name_plural': 'Записи на курс'},
        ),
        migrations.AlterField(
            model_name='quiz',
            name='type',
            field=models.CharField(choices=[('c', 'Common'), ('e', 'Exam'), ('e', 'Lesson')], default='c', max_length=1, null=True, verbose_name='Тип'),
        ),
        migrations.CreateModel(
            name='ContentQuiz',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contentquiz_related', to=settings.AUTH_USER_MODEL)),
                ('quiz', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='appcourses.Quiz')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
