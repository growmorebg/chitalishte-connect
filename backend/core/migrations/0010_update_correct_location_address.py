from django.db import migrations


NEW_ADDRESS_LINE = "кв. Враждебна, ул. „8-ма“ 47"
NEW_CITY = "София"
NEW_POSTAL_CODE = "1839"


def update_correct_location_address(apps, schema_editor):
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
        ("core", "0009_update_default_location_address"),
    ]

    operations = [
        migrations.RunPython(update_correct_location_address, migrations.RunPython.noop),
    ]
