# Generated by Django 3.1.3 on 2023-04-11 10:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0031_auto_20230411_1007'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='episode',
            name='comments',
        ),
    ]