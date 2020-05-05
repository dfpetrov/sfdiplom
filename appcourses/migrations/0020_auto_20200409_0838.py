# Generated by Django 3.0.3 on 2020-04-09 05:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appcourses', '0019_auto_20200409_0835'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='courseskillitem',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='courseskillitem',
            name='object_id',
        ),
        migrations.AddField(
            model_name='courseskillitem',
            name='course',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='skills', to='appcourses.Course'),
        ),
        migrations.AlterField(
            model_name='course',
            name='overview',
            field=models.CharField(max_length=200, verbose_name='Краткое описание'),
        ),
        migrations.AlterField(
            model_name='courseskillitem',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Название'),
        ),
    ]