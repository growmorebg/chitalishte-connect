from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from core.models import OrderedModel, PublishableModel, SeoFieldsMixin, TimeStampedModel


class StoryType(models.TextChoices):
    STORY = "story", "История"
    PROJECT = "project", "Проект"
    NEWS = "news", "Новина"


class Story(SeoFieldsMixin, PublishableModel, OrderedModel, TimeStampedModel):
    story_type = models.CharField(
        "Тип",
        max_length=16,
        choices=StoryType.choices,
        default=StoryType.PROJECT,
        db_column="project_type",
    )
    title = models.CharField("Заглавие", max_length=180)
    slug = models.SlugField("Кратък адрес", unique=True)
    excerpt = models.TextField("Кратко резюме")
    body = models.TextField("Съдържание")
    cover_image = models.ImageField("Изображение", upload_to="projects/", blank=True, null=True)
    published_at = models.DateField("Дата на публикуване")
    is_featured = models.BooleanField("Показвай на началната страница", default=True)

    class Meta:
        db_table = "cms_project"
        ordering = ["sort_order", "-published_at", "-id"]
        verbose_name = "Публикация"
        verbose_name_plural = "Публикации"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("cms:project_detail", kwargs={"slug": self.slug})

    def get_project_type_display(self):
        return self.get_story_type_display()


class StoryAttachment(OrderedModel):
    story = models.ForeignKey(
        Story,
        on_delete=models.CASCADE,
        related_name="attachments",
        db_column="project_id",
    )
    title = models.CharField("Заглавие", max_length=180)
    file = models.FileField("Файл", upload_to="project_attachments/", blank=True, null=True)
    external_url = models.URLField("Външен адрес", blank=True)
    description = models.CharField("Описание", max_length=220, blank=True)

    class Meta:
        db_table = "cms_projectattachment"
        ordering = ["sort_order", "id"]
        verbose_name = "Файл към публикация"
        verbose_name_plural = "Файлове към публикации"

    def clean(self):
        super().clean()
        if not self.file and not self.external_url:
            raise ValidationError("Добавете файл или външен адрес.")

    def __str__(self):
        return self.title

# Create your models here.
