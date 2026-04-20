from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.models import OrderedModel, PublishableModel, SeoFieldsMixin, SingletonModel, TimeStampedModel


class HomePage(SeoFieldsMixin, SingletonModel, TimeStampedModel):
    hero_badge = models.CharField("Бадж в хедъра", max_length=120, default="ОТВОРЕНО ЗА ЦЯЛОТО СЕМЕЙСТВО")
    hero_title = models.CharField(
        "Основно заглавие",
        max_length=220,
        default="Съвременна читалищна платформа за изкуство, обучение и общност.",
    )
    hero_body = models.TextField(
        "Текст в хедъра",
        default=(
            "Публична начална страница за програми, новини, контакти и записвания, "
            "която може да се поддържа изцяло от администрацията."
        ),
    )
    hero_image = models.ImageField(
        "Снимка в хедъра",
        upload_to="home/",
        blank=True,
        null=True,
        help_text="Показва се като основна снимка в началната секция и заменя текстовия hero блок.",
    )
    hero_image_alt = models.CharField(
        "Alt текст на снимката",
        max_length=220,
        blank=True,
        help_text="Кратко описание на снимката за достъпност.",
    )
    primary_cta_label = models.CharField("Основен бутон", max_length=80, default="Разгледайте програмите")
    primary_cta_url = models.CharField("Адрес на основния бутон", max_length=220, default="/programs/")
    secondary_cta_label = models.CharField("Втори бутон", max_length=80, default="Новини")
    secondary_cta_url = models.CharField("Адрес на втория бутон", max_length=220, default="/novini/")
    mission_title = models.CharField("Заглавие на мисията", max_length=160, default="Какво изграждаме")
    mission_body = models.TextField(
        "Текст за мисията",
        default=(
            "Място за обучение, сцена за местни проекти и достъпна културна услуга за деца, "
            "младежи и възрастни."
        ),
    )
    programs_heading = models.CharField("Заглавие на програмите", max_length=160, default="Школи и клубове")
    programs_intro = models.TextField(
        "Увод към програмите",
        default="Организирайте програмите по категории, преподаватели, графици и ценови планове.",
    )
    stories_heading = models.CharField(
        "Заглавие на публикациите",
        max_length=160,
        default="Новини",
        db_column="projects_heading",
    )
    stories_intro = models.TextField(
        "Увод към публикациите",
        default="Публикувайте всички новини и публикации в един общ архив.",
        db_column="projects_intro",
    )
    contacts_heading = models.CharField("Заглавие на контактната секция", max_length=160, blank=True)
    contacts_intro = models.TextField("Увод към контактната секция", blank=True)

    class Meta:
        db_table = "cms_homepage"
        verbose_name = "Начална страница"
        verbose_name_plural = "Начална страница"

    def __str__(self):
        return "Начална страница"

    @property
    def projects_heading(self):
        return self.stories_heading

    @property
    def projects_intro(self):
        return self.stories_intro


class HomeMetric(OrderedModel):
    home_page = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name="stats")
    value = models.CharField("Стойност", max_length=32)
    label = models.CharField("Етикет", max_length=120)
    description = models.CharField("Описание", max_length=220, blank=True)

    class Meta:
        db_table = "cms_homestat"
        ordering = ["sort_order", "id"]
        verbose_name = "Метрика на началната страница"
        verbose_name_plural = "Метрики на началната страница"

    def __str__(self):
        return f"{self.label}: {self.value}"


class HomeFeature(OrderedModel):
    home_page = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name="features")
    eyebrow = models.CharField("Кратък надпис", max_length=64, blank=True)
    title = models.CharField("Заглавие", max_length=120)
    description = models.TextField("Описание")

    class Meta:
        db_table = "cms_homefeature"
        ordering = ["sort_order", "id"]
        verbose_name = "Акцент на началната страница"
        verbose_name_plural = "Акценти на началната страница"

    def __str__(self):
        return self.title


class PageType(models.TextChoices):
    STANDARD = "standard", "Стандартна страница"
    HISTORY = "history", "История"
    GOVERNANCE = "governance", "Настоятелство и екип"
    MEMBERSHIP = "membership", "Членство"
    CHARTER = "charter", "Устав"
    PRIVACY = "privacy", "Поверителност"
    COOKIES = "cookies", "Бисквитки"


class Page(SeoFieldsMixin, PublishableModel, OrderedModel, TimeStampedModel):
    page_type = models.CharField(
        "Тип",
        max_length=16,
        choices=PageType.choices,
        default=PageType.STANDARD,
    )
    title = models.CharField("Заглавие", max_length=180)
    navigation_title = models.CharField("Кратко заглавие в навигацията", max_length=80, blank=True)
    slug = models.SlugField("Кратък адрес", unique=True)
    intro = models.TextField("Увод", blank=True)
    body = models.TextField("Съдържание")
    callout_title = models.CharField("Заглавие на акцент", max_length=180, blank=True)
    callout_body = models.TextField("Текст на акцент", blank=True)
    show_in_header = models.BooleanField("Показвай в главното меню", default=False)
    show_in_footer = models.BooleanField("Показвай във футъра", default=False)

    class Meta:
        db_table = "cms_staticpage"
        ordering = ["sort_order", "title"]
        verbose_name = "Страница"
        verbose_name_plural = "Страници"

    def __str__(self):
        return self.title

    @property
    def is_legal_page(self):
        return self.page_type in {PageType.CHARTER, PageType.PRIVACY, PageType.COOKIES}

    def get_absolute_url(self):
        if self.slug == "history":
            return reverse("cms:history")
        if self.slug == "library":
            return reverse("cms:library")
        if self.slug in {"board", "leadership"}:
            return reverse("cms:board")
        if self.slug == "privacy":
            return reverse("cms:privacy")
        if self.slug == "cookies":
            return reverse("cms:cookies")
        return reverse("cms:page_detail", kwargs={"slug": self.slug})


class HistoryEntry(PublishableModel, OrderedModel, TimeStampedModel):
    page = models.ForeignKey("pages.Page", on_delete=models.CASCADE, related_name="history_entries", verbose_name="Страница")
    title = models.CharField("Заглавие", max_length=180)
    slug = models.SlugField("Кратък адрес", unique=True, blank=True)
    period_label = models.CharField("Период", max_length=80, blank=True)
    summary = models.TextField("Кратко резюме", blank=True)
    body = models.TextField("Съдържание", blank=True)
    image = models.ImageField("Изображение", upload_to="history/", blank=True, null=True)

    class Meta:
        ordering = ["sort_order", "title"]
        verbose_name = "Исторически запис"
        verbose_name_plural = "История"

    def __str__(self):
        return self.title

    def _generate_unique_slug(self):
        base_slug = slugify(self.title) or "history-image"
        slug = base_slug
        index = 2
        queryset = type(self).objects.all()
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)

        while queryset.filter(slug=slug).exists():
            slug = f"{base_slug}-{index}"
            index += 1

        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._generate_unique_slug()
        super().save(*args, **kwargs)


class LibraryImage(PublishableModel, OrderedModel):
    page = models.ForeignKey("pages.Page", on_delete=models.CASCADE, related_name="library_images", verbose_name="Страница")
    image = models.ImageField("Изображение", upload_to="library/")
    caption = models.CharField("Надпис", max_length=220, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "Снимка към библиотеката"
        verbose_name_plural = "Снимки към библиотеката"

    def __str__(self):
        if self.caption:
            return self.caption
        return str(self.image) if self.image else "—"


class BoardMember(PublishableModel, OrderedModel, TimeStampedModel):
    full_name = models.CharField("Име", max_length=160)
    slug = models.SlugField("Кратък адрес", unique=True)
    role = models.CharField("Роля", max_length=160)
    short_bio = models.TextField("Кратка биография", blank=True)
    biography = models.TextField("Подробна биография", blank=True)
    portrait = models.ImageField("Портрет", upload_to="leadership/", blank=True, null=True)
    email = models.EmailField("Имейл", blank=True)
    phone = models.CharField("Телефон", max_length=120, blank=True, db_column="term_label")

    class Meta:
        db_table = "cms_leadershipmember"
        ordering = ["sort_order", "full_name"]
        verbose_name = "Член на настоятелството"
        verbose_name_plural = "Настоятелство и екип"

    def __str__(self):
        return f"{self.full_name} - {self.role}"


class GalleryImage(PublishableModel, OrderedModel):
    image = models.ImageField(
        "Изображение",
        upload_to="gallery/",
        help_text="Качете файл от компютъра си.",
    )
    caption = models.CharField("Надпис", max_length=500, blank=True)
    alt_text = models.CharField("Alt текст", max_length=220, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cms_galleryimage"
        ordering = ["sort_order", "id"]
        verbose_name = "Снимка от галерията"
        verbose_name_plural = "Галерия"

    def __str__(self):
        if self.caption:
            return self.caption
        return str(self.image) if self.image else "—"

# Create your models here.
