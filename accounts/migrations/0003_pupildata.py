# Generated by Django 4.2.3 on 2023-08-23 05:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_customuser_jwt_token'),
    ]

    operations = [
        migrations.CreateModel(
            name='PupilData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('learners_id_number', models.CharField(blank=True, max_length=200, null=True)),
                ('gender', models.CharField(blank=True, max_length=200, null=True)),
                ('age', models.CharField(blank=True, max_length=200, null=True)),
                ('level', models.CharField(blank=True, max_length=200, null=True)),
                ('Teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='teacher', to=settings.AUTH_USER_MODEL)),
                ('User', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='pupil', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
