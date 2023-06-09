# Generated by Django 4.1.8 on 2023-04-27 01:10

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("golf_contest", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tournament",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("start_date", models.DateField()),
                (
                    "state",
                    models.CharField(
                        choices=[
                            ("NST", "Not Started"),
                            ("RD1", "Round 1"),
                            ("RD2", "Round 2"),
                            ("RD3", "Round 3"),
                            ("RD4", "Round 4"),
                            ("FNL", "FINAL"),
                        ],
                        max_length=3,
                    ),
                ),
                ("world_ranking_week", models.SmallIntegerField(default=1)),
            ],
        ),
        migrations.AlterField(
            model_name="golfer",
            name="rd_four_tee_time",
            field=models.TimeField(default="8:00"),
        ),
        migrations.AlterField(
            model_name="golfer",
            name="rd_one_tee_time",
            field=models.TimeField(default="8:00"),
        ),
        migrations.AlterField(
            model_name="golfer",
            name="rd_three_tee_time",
            field=models.TimeField(default="8:00"),
        ),
        migrations.AlterField(
            model_name="golfer",
            name="rd_two_tee_time",
            field=models.TimeField(default="8:00"),
        ),
    ]
