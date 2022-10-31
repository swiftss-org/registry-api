# Generated by Django 3.1.3 on 2022-10-29 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registry', '0016_auto_20220222_1415'),
    ]

    operations = [
        migrations.AlterField(
            model_name='episode',
            name='episode_type',
            field=models.CharField(choices=[('INGUINAL', 'Inguinal Mesh Hernia Repair'), ('INCISIONAL', 'Incisional Mesh Hernia Repair'), ('FEMORAL', 'Femoral Mesh Hernia Repair'), ('UMBILICAL', 'Umbilical/Periumbilicial Mesh Hernia Repair')], max_length=128),
        ),
    ]
