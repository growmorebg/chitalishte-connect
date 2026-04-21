from django.db import migrations, models


NEW_EMAIL = "chitalishtevrajdebna@gmail.com"
NEW_PHONE_PRIMARY = "087 782 0388"
OLD_EMAIL = "hello@example.bg"
OLD_PHONE_PRIMARY_VALUES = [
    "+359 88 000 0000",
    "+359880000000",
]
OLD_PHONE_SECONDARY = "+359 88 000 0001"


def update_default_contact_details(apps, schema_editor):
    SiteSettings = apps.get_model("core", "SiteSettings")
    SiteSettings.objects.filter(phone_primary__in=OLD_PHONE_PRIMARY_VALUES).update(
        phone_primary=NEW_PHONE_PRIMARY
    )
    SiteSettings.objects.filter(phone_secondary=OLD_PHONE_SECONDARY).update(phone_secondary="")
    SiteSettings.objects.filter(email=OLD_EMAIL).update(email=NEW_EMAIL)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_update_site_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="phone_primary",
            field=models.CharField(
                default=NEW_PHONE_PRIMARY,
                max_length=64,
                verbose_name="Основен телефон",
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="email",
            field=models.EmailField(default=NEW_EMAIL, max_length=254, verbose_name="Имейл"),
        ),
        migrations.RunPython(update_default_contact_details, migrations.RunPython.noop),
    ]
