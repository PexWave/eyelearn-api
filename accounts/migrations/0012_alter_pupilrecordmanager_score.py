# Generated by Django 4.2.3 on 2023-12-05 01:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_remove_pupilrecordmanager_category_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pupilrecordmanager',
            name='score',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
