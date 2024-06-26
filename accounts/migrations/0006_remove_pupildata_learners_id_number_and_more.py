# Generated by Django 4.2.3 on 2023-11-12 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_customuser_school'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pupildata',
            name='learners_id_number',
        ),
        migrations.AddField(
            model_name='pupildata',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='pupildata',
            name='nickname',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='jwt_token',
            field=models.TextField(blank=True, null=True, unique=True),
        ),
    ]
