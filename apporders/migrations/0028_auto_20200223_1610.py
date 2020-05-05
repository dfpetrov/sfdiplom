# Generated by Django 3.0.2 on 2020-02-23 13:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apporders', '0027_orderfavourites_orderlike'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkpointorderitem',
            name='order_in_check',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_in_check_checkpoint', to='apporders.OrderInCheck'),
        ),
    ]
