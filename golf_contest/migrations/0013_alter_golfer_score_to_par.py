# Generated by Django 4.2.1 on 2023-05-09 02:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("golf_contest", "0012_alter_golfer_tournament_position"),
    ]

    operations = [
        migrations.AlterField(
            model_name="golfer",
            name="score_to_par",
            field=models.SmallIntegerField(blank=True, default=None, null=True),
        ),
    ]
