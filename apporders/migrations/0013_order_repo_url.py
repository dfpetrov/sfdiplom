# Generated by Django 3.0.2 on 2020-01-23 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apporders', '0012_order_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='repo_url',
            field=models.TextField(default='', null=True, verbose_name='Комментарий'),
        ),
    ]