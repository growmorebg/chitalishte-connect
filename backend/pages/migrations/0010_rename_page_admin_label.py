from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0009_libraryimage"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="page",
            options={
                "ordering": ["sort_order", "title"],
                "verbose_name": "Страница",
                "verbose_name_plural": "За Нас",
            },
        ),
    ]
