# Generated by Django 4.2.1 on 2023-05-19 15:36

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("golf_contest", "0023_golfer_tournament_position_tied_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="golfer",
            options={"ordering": ["name"]},
        ),
    ]
