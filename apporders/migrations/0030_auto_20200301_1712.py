# Generated by Django 3.0.3 on 2020-03-01 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apporders', '0029_order_comment_html'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='comment',
            field=models.TextField(blank=True, default='', max_length=5000, null=True, verbose_name='Комментарий'),
        ),
    ]
