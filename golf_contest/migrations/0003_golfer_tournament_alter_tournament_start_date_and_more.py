# Generated by Django 4.1.8 on 2023-04-27 02:21

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("golf_contest", "0002_tournament_alter_golfer_rd_four_tee_time_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="golfer",
            name="tournament",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="golf_contest.tournament"
            ),
        ),
        migrations.AlterField(
            model_name="tournament",
            name="start_date",
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name="tournament",
            name="state",
            field=models.CharField(
                choices=[
                    ("NST", "Not Started"),
                    ("RD1", "Round 1"),
                    ("RD2", "Round 2"),
                    ("RD3", "Round 3"),
                    ("RD4", "Round 4"),
                    ("FNL", "FINAL"),
                ],
                default="NST",
                max_length=3,
            ),
        ),
    ]
