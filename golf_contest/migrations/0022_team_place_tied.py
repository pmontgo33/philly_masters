# Generated by Django 4.2.1 on 2023-05-17 23:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("golf_contest", "0021_tournament_tournament_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="place_tied",
            field=models.BooleanField(default=False),
        ),
    ]