# Generated by Django 3.0.2 on 2020-01-12 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apporders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('inprogress', 'В работе'), ('done', 'Done')], default='inprogress', max_length=50),
        ),
    ]
