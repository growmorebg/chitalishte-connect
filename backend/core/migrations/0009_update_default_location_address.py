from django.db import migrations, models


NEW_ADDRESS_LINE = "кв. Враждебна, ул. „8-ма“ 47"
NEW_CITY = "София"
NEW_POSTAL_CODE = "1839"


def update_known_placeholder_locations(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    SiteSettings.objects.filter(
        address_line__in=[
            "ул. Самодивска 12",
            "ул. 55-та №13, кв. Враждебна",
        ],
        city="София",
    ).update(
        address_line=NEW_ADDRESS_LINE,
        city=NEW_CITY,
        postal_code=NEW_POSTAL_CODE,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_remove_locationhour_location_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="address_line",
            field=models.CharField(default=NEW_ADDRESS_LINE, max_length=220, verbose_name="Адрес"),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="postal_code",
            field=models.CharField(blank=True, default=NEW_POSTAL_CODE, max_length=20, verbose_name="Пощенски код"),
        ),
        migrations.RunPython(update_known_placeholder_locations, migrations.RunPython.noop),
    ]
