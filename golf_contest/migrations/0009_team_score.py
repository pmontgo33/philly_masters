# Generated by Django 4.2.1 on 2023-05-08 14:37

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("golf_contest", "0008_alter_golfer_rd_four_tee_time_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="team",
            name="score",
            field=models.SmallIntegerField(default=0),
        ),
    ]
