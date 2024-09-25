from django.db import migrations


def get_primary_surgeon_from_episode_surgeons(apps, schema_editor):
    Episode = apps.get_model("registry", "episode")

    for episode in Episode.objects.all():
        print("\n Migrating episode's surgeons: ")
        print(episode.id)
        MedicalPersonnel = episode.surgeons
        surgeons = MedicalPersonnel.all()
        if len(surgeons) > 0:
            episode.primary_surgeon = surgeons[0]
        if len(surgeons) > 1:
            episode.secondary_surgeon = surgeons[1]
        if len(surgeons) > 2:
            episode.tertiary_surgeon = surgeons[2]
        episode.save()


class Migration(migrations.Migration):

    dependencies = [
        ("registry", "0039_episode_primary_surgeon"),
    ]

    operations = [
        migrations.RunPython(get_primary_surgeon_from_episode_surgeons)
    ]
