# Generated by Django 3.1.3 on 2024-02-28 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("registry", "0034_auto_20230808_0957"),
    ]

    operations = [
        migrations.AddField(
            model_name="episode",
            name="comments",
            field=models.TextField(blank=True, null=True),
        ),
    ]
