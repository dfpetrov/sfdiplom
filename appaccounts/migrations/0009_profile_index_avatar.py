# Generated by Django 3.0.3 on 2020-05-01 08:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appaccounts', '0008_profile_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='index_avatar',
            field=models.SmallIntegerField(blank=True, null=True, verbose_name='Индекс аватара'),
        ),
    ]
