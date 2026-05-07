from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_update_default_contact_details"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="contact_page_hours_label",
            field=models.CharField(
                default="Работно време",
                max_length=120,
                verbose_name="Етикет за работното време",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="contact_page_map_label",
            field=models.CharField(
                default="Карта за разположение:",
                max_length=160,
                verbose_name="Етикет за картата",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="contact_page_form_heading",
            field=models.CharField(
                default="За да изпратите съобщение, моля попълнете формата:",
                max_length=220,
                verbose_name="Заглавие над формата",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="contact_page_submit_label",
            field=models.CharField(
                default="Изпрати запитване",
                max_length=80,
                verbose_name="Текст на бутона за формата",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="contact_page_privacy_note",
            field=models.TextField(
                blank=True,
                default="Ще използваме данните ви само за обработка на това запитване.",
                verbose_name="Текст под формата",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="contact_page_success_message",
            field=models.CharField(
                default=(
                    "Благодарим. Съобщението ви беше изпратено успешно "
                    "и ще се свържем с вас при възможност."
                ),
                max_length=220,
                verbose_name="Съобщение при успешно изпращане",
            ),
        ),
    ]
