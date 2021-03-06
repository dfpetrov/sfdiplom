# # Generated by Django 3.0.2 on 2020-01-14 06:26

# import django.contrib.postgres.fields
# from django.db import migrations, models


# class Migration(migrations.Migration):

#     dependencies = [
#         ('apptasks', '0008_task_author_profile'),
#     ]

#     operations = [
#         migrations.AddField(
#             model_name='task',
#             name='chekpoints',
#             field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=200), blank=True, null=True, size=None),
#         ),
#     ]

# Generated by Django 3.0.2 on 2020-01-14 06:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apptasks', '0008_task_author_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='chekpoints',
            field=models.CharField(choices=[('active', 'Active'), ('inactive', 'Inactive')], default='chekpoints', max_length=50),
        ),
    ]
