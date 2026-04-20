from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0004_historyentry_page"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RenameField(
                    model_name="boardmember",
                    old_name="term_label",
                    new_name="phone",
                ),
                migrations.AlterField(
                    model_name="boardmember",
                    name="phone",
                    field=models.CharField(blank=True, db_column="term_label", max_length=120, verbose_name="Телефон"),
                ),
            ],
        ),
    ]
