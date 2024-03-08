# Generated by Django 3.1.3 on 2022-10-29 17:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registry", "0019_episode_size"),
    ]

    operations = [
        migrations.AddField(
            model_name="episode",
            name="antibiotic_type",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="episode",
            name="antibiotic_used",
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
