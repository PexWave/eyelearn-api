# Generated by Django 4.2.3 on 2023-10-12 04:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lessons', '0003_remove_level_lesson_level_lessons'),
    ]

    operations = [
        migrations.RenameField(
            model_name='lesson',
            old_name='lesson',
            new_name='lesson_audio',
        ),
    ]
