from django.db import migrations, models


def update_news_section_labels(apps, schema_editor):
    HomePage = apps.get_model("pages", "HomePage")
    HomeFeature = apps.get_model("pages", "HomeFeature")
    FooterLink = apps.get_model("core", "FooterLink")

    HomePage.objects.filter(
        stories_heading__in=["Проекти", "Проекти и новини"]
    ).update(stories_heading="Новини")
    HomePage.objects.filter(
        stories_intro__in=[
            "Публикувайте архив, активни инициативи и приложения към всяка публикация.",
            "Архив на инициативи, публикации и файлове за изтегляне.",
        ]
    ).update(stories_intro="Всички публикации са събрани в един общ архив.")
    HomePage.objects.filter(
        secondary_cta_label__in=["Проекти", "Проекти и новини"]
    ).update(secondary_cta_label="Новини")
    HomePage.objects.filter(secondary_cta_url="/projects/").update(secondary_cta_url="/novini/")

    HomeFeature.objects.filter(title="Проекти и новини").update(title="Новини")
    FooterLink.objects.filter(url="/projects/").update(url="/novini/")
    FooterLink.objects.filter(
        title__in=["Проекти", "Проекти и новини"],
        url__in=["/novini/", "/projects/"],
    ).update(title="Новини")


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0004_alter_sitesettings_working_hours_summary"),
        ("pages", "0007_homepage_hero_image_and_alt"),
    ]

    operations = [
        migrations.AlterField(
            model_name="homepage",
            name="secondary_cta_label",
            field=models.CharField(default="Новини", max_length=80, verbose_name="Втори бутон"),
        ),
        migrations.AlterField(
            model_name="homepage",
            name="secondary_cta_url",
            field=models.CharField(default="/novini/", max_length=220, verbose_name="Адрес на втория бутон"),
        ),
        migrations.AlterField(
            model_name="homepage",
            name="stories_heading",
            field=models.CharField(
                db_column="projects_heading",
                default="Новини",
                max_length=160,
                verbose_name="Заглавие на публикациите",
            ),
        ),
        migrations.AlterField(
            model_name="homepage",
            name="stories_intro",
            field=models.TextField(
                db_column="projects_intro",
                default="Публикувайте всички новини и публикации в един общ архив.",
                verbose_name="Увод към публикациите",
            ),
        ),
        migrations.RunPython(update_news_section_labels, migrations.RunPython.noop),
    ]
