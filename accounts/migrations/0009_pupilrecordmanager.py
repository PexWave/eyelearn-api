# Generated by Django 4.2.3 on 2023-12-03 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_tokenmanager'),
    ]

    operations = [
        migrations.CreateModel(
            name='PupilRecordManager',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(blank=True, max_length=200, null=True)),
                ('subcategory', models.CharField(blank=True, max_length=200, null=True)),
            ],
        ),
    ]
