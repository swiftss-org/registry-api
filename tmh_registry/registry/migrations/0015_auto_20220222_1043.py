# Generated by Django 3.1.3 on 2022-02-22 10:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registry", "0014_remove_episode_discharge_date"),
    ]

    operations = [
        migrations.RenameField(
            model_name="followup",
            old_name="follow_up_date",
            new_name="date",
        ),
        migrations.AddField(
            model_name="followup",
            name="created_at",
            field=models.DateField(auto_now_add=True, default="1998-1-1"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="followup",
            name="updated_at",
            field=models.DateField(auto_now=True),
        ),
    ]