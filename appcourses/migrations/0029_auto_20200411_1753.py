# Generated by Django 3.0.3 on 2020-04-11 14:53

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appcourses', '0028_auto_20200411_1633'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='language',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quizzes', to='appcourses.Language'),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quizzes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='quiz',
            name='subject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quizzes', to='appcourses.Subject'),
        ),
    ]
