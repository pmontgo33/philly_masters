# Generated by Django 4.2.1 on 2023-05-09 02:32

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("golf_contest", "0014_alter_golfer_rd_four_strokes_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="golfer",
            name="name",
            field=models.CharField(max_length=40),
        ),
    ]