# Generated by Django 4.2.10 on 2024-06-07 16:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Exercises', '0002_routineexercise_notes'),
    ]

    operations = [
        migrations.AddField(
            model_name='routineexercise',
            name='actions',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
