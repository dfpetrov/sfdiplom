# Generated by Django 3.0.2 on 2020-01-17 07:33

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('apporders', '0006_auto_20200116_1536'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderInCheck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('status', models.CharField(choices=[('incheck', 'Взять на проверку'), ('done', 'Проверен')], default='incheck', max_length=50)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='apporders.Order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Проверяемый заказ',
                'verbose_name_plural': 'Проверяемые заказы',
                'ordering': ('-created',),
            },
        ),
    ]
