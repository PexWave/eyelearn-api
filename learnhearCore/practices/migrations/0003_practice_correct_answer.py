# Generated by Django 4.2.3 on 2023-10-09 05:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('practices', '0002_remove_practice_practice_audio_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='practice',
            name='correct_answer',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
