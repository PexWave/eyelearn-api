# Generated by Django 4.2.3 on 2023-12-05 03:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_alter_pupilrecordmanager_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pupilrecordmanager',
            name='practice',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
