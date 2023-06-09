# Generated by Django 4.1.8 on 2023-04-28 01:29

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("golf_contest", "0004_alter_golfer_rd_four_tee_time_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="golfer",
            name="tournament",
        ),
        migrations.AddField(
            model_name="tournament",
            name="golfers",
            field=models.ManyToManyField(to="golf_contest.golfer"),
        ),
        migrations.AlterField(
            model_name="golfer",
            name="name",
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name="tournament",
            name="world_ranking_week",
            field=models.SmallIntegerField(default=0),
        ),
    ]
