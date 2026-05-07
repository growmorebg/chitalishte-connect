from django.db import migrations, models


NEW_SITE_NAME = 'Народно читалище „Св. св. Кирил и Методий – 1926“'
OLD_SITE_NAME = "Chitalishte Connect"


def update_site_name(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    SiteSettings.objects.filter(site_name=OLD_SITE_NAME).update(site_name=NEW_SITE_NAME)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_update_correct_location_address"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="site_name",
            field=models.CharField(default=NEW_SITE_NAME, max_length=160, verbose_name="Име на сайта"),
        ),
        migrations.RunPython(update_site_name, migrations.RunPython.noop),
    ]
