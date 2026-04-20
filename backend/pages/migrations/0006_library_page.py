from django.db import migrations


def create_library_page(apps, schema_editor):
    Page = apps.get_model("pages", "Page")
    Page.objects.get_or_create(
        slug="library",
        defaults={
            "page_type": "standard",
            "title": "Библиотека",
            "navigation_title": "Библиотека",
            "intro": "Публична секция за фонда, читателските инициативи и полезна информация за заемане.",
            "body": (
                "<p>Представете библиотечния фонд, текущите читателски клубове и "
                "новите заглавия, които посетителите могат да открият на място.</p>"
                "<p>Добавете информация за работното време, условията за заемане и "
                "възможностите за дарение на книги, когато са уточнени.</p>"
            ),
            "callout_title": "Как да използвате страницата",
            "callout_body": "Поддържайте описанието на фонда, услугите и специалните инициативи актуални.",
            "show_in_header": True,
            "show_in_footer": False,
            "is_published": True,
            "sort_order": 2,
        },
    )


def remove_library_page(apps, schema_editor):
    Page = apps.get_model("pages", "Page")
    Page.objects.filter(slug="library").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0005_rename_boardmember_term_label_to_phone"),
    ]

    operations = [
        migrations.RunPython(create_library_page, remove_library_page),
    ]
