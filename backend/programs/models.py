from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from core.models import OrderedModel, PublishableModel, SeoFieldsMixin, TimeStampedModel


class ProgramCategory(SeoFieldsMixin, PublishableModel, OrderedModel):
    name = models.CharField("Име", max_length=120)
    slug = models.SlugField("Кратък адрес", unique=True)
    description = models.TextField("Описание", blank=True)

    class Meta:
        db_table = "cms_programcategory"
        ordering = ["sort_order", "name"]
        verbose_name = "Категория школи"
        verbose_name_plural = "Категории школи"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("cms:program_category", kwargs={"slug": self.slug})


class Instructor(PublishableModel, OrderedModel, TimeStampedModel):
    full_name = models.CharField("Име", max_length=160)
    slug = models.SlugField("Кратък адрес", unique=True)
    role_title = models.CharField("Роля", max_length=160)
    biography = models.TextField("Биография")
    credentials = models.TextField("Квалификации", blank=True)
    portrait = models.ImageField("Портрет", upload_to="instructors/", blank=True, null=True)
    email = models.EmailField("Имейл", blank=True)
    phone = models.CharField("Телефон", max_length=64, blank=True)

    class Meta:
        db_table = "cms_instructor"
        ordering = ["sort_order", "full_name"]
        verbose_name = "Преподавател"
        verbose_name_plural = "Преподаватели"

    def __str__(self):
        return self.full_name


class Program(SeoFieldsMixin, PublishableModel, OrderedModel, TimeStampedModel):
    category = models.ForeignKey(
        ProgramCategory,
        on_delete=models.PROTECT,
        related_name="programs",
        verbose_name="Категория",
    )
    instructors = models.ManyToManyField(
        Instructor,
        blank=True,
        related_name="programs",
        verbose_name="Преподаватели",
        db_table="cms_program_instructors",
    )
    title = models.CharField("Заглавие", max_length=160)
    slug = models.SlugField("Кратък адрес", unique=True)
    summary = models.TextField("Кратко описание")
    description = models.TextField("Подробно описание")
    audience = models.CharField("Подходящо за", max_length=160, blank=True)
    duration = models.CharField("Продължителност", max_length=120, blank=True)
    age_group = models.CharField("Възрастова група", max_length=120, blank=True)
    level = models.CharField("Ниво", max_length=120, blank=True)
    location_name = models.CharField("Локация", max_length=160, blank=True)
    inquiry_phone = models.CharField(
        "Телефон за записване",
        max_length=64,
        blank=True,
        help_text="Оставете празно, за да се използва основният телефон от глобалните настройки.",
    )
    inquiry_email = models.EmailField("Имейл за записване", blank=True)
    cta_label = models.CharField("Текст на бутона", max_length=80, default="Изпрати запитване")
    cover_image = models.ImageField("Основно изображение", upload_to="programs/", blank=True, null=True)
    is_featured = models.BooleanField("Показвай на началната страница", default=True)

    class Meta:
        db_table = "cms_program"
        ordering = ["sort_order", "title"]
        verbose_name = "Школа"
        verbose_name_plural = "Школи"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("cms:program_detail", kwargs={"slug": self.slug})


class ProgramSchedule(OrderedModel):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="schedule_entries")
    title = models.CharField("Етикет", max_length=120, blank=True)
    day_label = models.CharField("Ден", max_length=64)
    start_time = models.TimeField("Начало")
    end_time = models.TimeField("Край")
    room = models.CharField("Зала или локация", max_length=120, blank=True)
    notes = models.CharField("Бележка", max_length=220, blank=True)

    class Meta:
        db_table = "cms_programschedule"
        ordering = ["sort_order", "id"]
        verbose_name = "График"
        verbose_name_plural = "Графици"

    def __str__(self):
        return f"{self.program} - {self.day_label}"


class PricingBlock(OrderedModel):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="pricing_options")
    title = models.CharField("План", max_length=120)
    price_label = models.CharField("Цена", max_length=64)
    billing_period = models.CharField("Период", max_length=120, blank=True)
    description = models.TextField("Описание", blank=True)
    is_featured = models.BooleanField("Подчертай", default=False)

    class Meta:
        db_table = "cms_programpricing"
        ordering = ["sort_order", "id"]
        verbose_name = "Ценови блок"
        verbose_name_plural = "Ценови блокове"

    def __str__(self):
        return f"{self.program} - {self.title}"


class ProgramGalleryImage(OrderedModel):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name="gallery_items")
    image = models.ImageField("Изображение", upload_to="program_gallery/")
    caption = models.CharField("Надпис", max_length=220, blank=True)

    class Meta:
        db_table = "cms_programgalleryimage"
        ordering = ["sort_order", "id"]
        verbose_name = "Снимка от галерия на школа"
        verbose_name_plural = "Галерии на школи"

    def __str__(self):
        return self.caption or f"Изображение #{self.pk}"


class ProgramSession(PublishableModel, OrderedModel, TimeStampedModel):
    program = models.ForeignKey(
        Program,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sessions",
        verbose_name="Школа",
    )
    title = models.CharField("Заглавие", max_length=255)
    date = models.DateField("Дата")
    time = models.TimeField("Начало")
    end_time = models.TimeField("Край", blank=True, null=True)
    description = models.TextField("Описание", blank=True)
    category = models.CharField("Етикет", max_length=120, blank=True)
    image = models.ImageField(
        "Изображение",
        upload_to="events/",
        blank=True,
        null=True,
        help_text="Качете файл от компютъра си.",
    )
    attendees = models.PositiveIntegerField("Участници", default=0)
    location_name = models.CharField("Локация", max_length=160, blank=True)

    class Meta:
        db_table = "cms_event"
        ordering = ["date", "time", "sort_order"]
        verbose_name = "Сесия или събитие"
        verbose_name_plural = "Сесии и събития"

    def __str__(self):
        return f"{self.title} ({self.date})"

    def clean(self):
        super().clean()
        if self.end_time and self.end_time <= self.time:
            raise ValidationError("Крайният час трябва да е след началния.")

# Create your models here.
