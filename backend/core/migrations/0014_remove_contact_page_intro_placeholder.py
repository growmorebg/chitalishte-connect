from django.db import migrations, models


PLACEHOLDER_INTRO = (
    "Всички публични контакти са събрани на едно място, заедно с карта, "
    "работно време и директен вход за въпроси."
)


def remove_placeholder_intro(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    SiteSettings.objects.filter(contact_page_intro=PLACEHOLDER_INTRO).update(contact_page_intro="")


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_contact_page_editable_content"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="contact_page_intro",
            field=models.TextField(blank=True, default="", verbose_name="Увод на контактната страница"),
        ),
        migrations.RunPython(remove_placeholder_intro, migrations.RunPython.noop),
    ]
