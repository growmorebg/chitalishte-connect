from django.core.exceptions import ValidationError
from django.db import models


class PublishedQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True)


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class OrderedModel(models.Model):
    sort_order = models.PositiveSmallIntegerField("Ред", default=0)

    class Meta:
        abstract = True


class PublishableModel(models.Model):
    objects = PublishedQuerySet.as_manager()

    is_published = models.BooleanField("Публикувано", default=True)

    class Meta:
        abstract = True


class SeoFieldsMixin(models.Model):
    seo_title = models.CharField(
        "SEO заглавие",
        max_length=160,
        blank=True,
        help_text="По желание заменя стандартното заглавие в търсачки и споделяне.",
    )
    seo_description = models.TextField(
        "SEO описание",
        blank=True,
        help_text="Кратко описание за търсачки, социални мрежи и линк превюта.",
    )
    seo_image = models.ImageField(
        "SEO изображение",
        upload_to="seo/",
        blank=True,
        null=True,
        help_text="Използва се при споделяне в социални мрежи, когато има нужда от отделно изображение.",
    )

    class Meta:
        abstract = True


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        model = type(self)
        if not self.pk and model.objects.exists():
            raise ValidationError("Разрешен е само един запис от този тип.")

    @classmethod
    def load(cls):
        return cls.objects.first() or cls()


class SiteSettings(SeoFieldsMixin, SingletonModel, TimeStampedModel):
    site_name = models.CharField(
        "Име на сайта",
        max_length=160,
        default='Народно читалище „Св. св. Кирил и Методий – 1926“',
    )
    site_tagline = models.CharField(
        "Кратък слоган",
        max_length=220,
        default="Културни програми, общност и съвременни читалищни услуги.",
    )
    footer_summary = models.TextField(
        "Резюме във футъра",
        blank=True,
        default=(
            "Примерно съдържание за културен център. Заменете го от администрацията "
            "с реалните текстове, контакти и правни страници."
        ),
    )
    location_name = models.CharField("Име на локацията", max_length=160, default="Основна база")
    location_short_description = models.TextField("Кратко описание на локацията", blank=True)
    address_line = models.CharField("Адрес", max_length=220, default="кв. Враждебна, ул. „8-ма“ 47")
    city = models.CharField("Град", max_length=120, default="София")
    postal_code = models.CharField("Пощенски код", max_length=20, blank=True, default="1839")
    phone_primary = models.CharField("Основен телефон", max_length=64, default="087 782 0388")
    phone_secondary = models.CharField("Допълнителен телефон", max_length=64, blank=True)
    email = models.EmailField("Имейл", default="chitalishtevrajdebna@gmail.com")
    contact_page_title = models.CharField(
        "Заглавие на контактната страница",
        max_length=160,
        default="Контакти",
    )
    contact_page_intro = models.TextField(
        "Увод на контактната страница",
        blank=True,
        default="",
    )
    contact_page_hours_label = models.CharField(
        "Етикет за работното време",
        max_length=120,
        default="Работно време",
    )
    contact_page_map_label = models.CharField(
        "Етикет за картата",
        max_length=160,
        default="Карта за разположение:",
    )
    contact_page_form_heading = models.CharField(
        "Заглавие над формата",
        max_length=220,
        default="За да изпратите съобщение, моля попълнете формата:",
    )
    contact_page_submit_label = models.CharField(
        "Текст на бутона за формата",
        max_length=80,
        default="Изпрати запитване",
    )
    contact_page_privacy_note = models.TextField(
        "Текст под формата",
        blank=True,
        default="Ще използваме данните ви само за обработка на това запитване.",
    )
    contact_page_success_message = models.CharField(
        "Съобщение при успешно изпращане",
        max_length=220,
        default="Благодарим. Съобщението ви беше изпратено успешно и ще се свържем с вас при възможност.",
    )
    working_hours_summary = models.CharField(
        "Резюме на работното време",
        max_length=160,
        default="Понеделник - петък, 09:00 - 18:00",
    )
    map_embed_url = models.URLField(
        "Вграден адрес за карта",
        blank=True,
        max_length=1200,
        help_text="OpenStreetMap или Google Maps embed адрес.",
    )
    location_access_notes = models.TextField("Допълнителна информация за достъп", blank=True)
    copyright_notice = models.CharField(
        "Авторски текст",
        max_length=220,
        default='© 2026 Народно читалище „Св. св. Кирил и Методий – 1926“. Всички права запазени.',
    )
    cookie_banner_title = models.CharField(
        "Заглавие на банера за бисквитки",
        max_length=120,
        default="Настройки за бисквитки",
    )
    cookie_banner_text = models.TextField(
        "Текст на банера за бисквитки",
        default=(
            "Използваме само необходимите бисквитки по подразбиране. Можете да приемете "
            "и допълнителни аналитични бисквитки или да прочетете подробностите в правните страници."
        ),
    )

    class Meta:
        db_table = "cms_sitesettings"
        verbose_name = "Глобални настройки"
        verbose_name_plural = "Глобални настройки"

    def __str__(self):
        return self.site_name


class FooterLink(PublishableModel, OrderedModel, TimeStampedModel):
    title = models.CharField("Етикет", max_length=120)
    url = models.CharField("Адрес", max_length=220)
    open_in_new_tab = models.BooleanField("Отвори в нов прозорец", default=False)

    class Meta:
        db_table = "cms_footerlink"
        ordering = ["sort_order", "title", "id"]
        verbose_name = "Връзка във футъра"
        verbose_name_plural = "Връзки във футъра"

    def __str__(self):
        return self.title

# Create your models here.
