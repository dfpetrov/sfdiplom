# Generated by Django 3.0.3 on 2020-04-15 18:02

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appcourses', '0046_auto_20200414_2158'),
        ('apppermission', '0004_lessonpermission'),
    ]

    operations = [
        migrations.CreateModel(
            name='ModulePermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_type', models.ManyToManyField(to='apppermission.AccessType', verbose_name='Тип доступа')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='permissions', to='appcourses.Module')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='module_permissions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Разрешение на модуль',
                'verbose_name_plural': 'Разрешения на модули',
            },
        ),
    ]
