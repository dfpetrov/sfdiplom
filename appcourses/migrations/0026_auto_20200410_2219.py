# Generated by Django 3.0.3 on 2020-04-10 19:19

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('appcourses', '0025_auto_20200410_1647'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='courses', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='courseenroll',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses_enroll', to='appcourses.Course'),
        ),
        migrations.AlterField(
            model_name='courseenroll',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='courses_enroll', to=settings.AUTH_USER_MODEL),
        ),
    ]
