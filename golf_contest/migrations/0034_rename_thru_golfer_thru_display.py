# Generated by Django 4.2.1 on 2023-05-26 18:43

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("golf_contest", "0033_golfer_status_alter_golfer_rounds"),
    ]

    operations = [
        migrations.RenameField(
            model_name="golfer",
            old_name="thru",
            new_name="thru_display",
        ),
    ]