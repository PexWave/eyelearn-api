# Generated by Django 4.2.3 on 2023-08-22 06:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='jwt_token',
            field=models.TextField(blank=True, null=True),
        ),
    ]
