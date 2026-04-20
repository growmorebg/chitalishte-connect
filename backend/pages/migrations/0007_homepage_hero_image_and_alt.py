from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0006_library_page"),
    ]

    operations = [
        migrations.AddField(
            model_name="homepage",
            name="hero_image",
            field=models.ImageField(
                blank=True,
                help_text="Показва се като основна снимка в началната секция и заменя текстовия hero блок.",
                null=True,
                upload_to="home/",
                verbose_name="Снимка в хедъра",
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="hero_image_alt",
            field=models.CharField(
                blank=True,
                help_text="Кратко описание на снимката за достъпност.",
                max_length=220,
                verbose_name="Alt текст на снимката",
            ),
        ),
    ]
