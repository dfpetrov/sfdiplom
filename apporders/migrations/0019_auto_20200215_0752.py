# Generated by Django 3.0.2 on 2020-02-15 04:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apptasks', '0026_auto_20200213_1203'),
        ('apporders', '0018_auto_20200213_1203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='task',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_task', to='apptasks.Task'),
        ),
    ]
