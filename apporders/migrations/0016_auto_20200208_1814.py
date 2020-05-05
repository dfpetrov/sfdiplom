# Generated by Django 3.0.2 on 2020-02-08 15:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apporders', '0015_orderincheck_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='cloud_url',
            field=models.URLField(blank=True, null=True, verbose_name='Cloud url'),
        ),
        migrations.AddField(
            model_name='order',
            name='github_pages_url',
            field=models.URLField(blank=True, null=True, verbose_name='Github pages'),
        ),
        migrations.AddField(
            model_name='order',
            name='github_repo_url',
            field=models.URLField(blank=True, null=True, verbose_name='Github репозиторий'),
        ),
        migrations.AddField(
            model_name='order',
            name='heroku_url',
            field=models.URLField(blank=True, null=True, verbose_name='Heroku url'),
        ),
    ]