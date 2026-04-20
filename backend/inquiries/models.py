from django.db import models
from django.urls import reverse

from core.models import TimeStampedModel


class InquiryType(models.TextChoices):
    GENERAL = "general", "Общо запитване"
    ENROLLMENT = "enrollment", "Записване"
    PARTNERSHIP = "partnership", "Партньорство"
    MEDIA = "media", "Медийно запитване"


class InquiryStatus(models.TextChoices):
    NEW = "new", "Ново"
    REVIEWED = "reviewed", "Прегледано"
    CLOSED = "closed", "Приключено"


class InquirySubmission(TimeStampedModel):
    inquiry_type = models.CharField(
        "Вид",
        max_length=16,
        choices=InquiryType.choices,
        default=InquiryType.GENERAL,
    )
    program = models.ForeignKey(
        "programs.Program",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="inquiries",
        verbose_name="Школа",
    )
    full_name = models.CharField("Име", max_length=160)
    email = models.EmailField("Имейл")
    phone = models.CharField("Телефон", max_length=64, blank=True)
    subject = models.CharField("Тема", max_length=180)
    message = models.TextField("Съобщение")
    admin_notes = models.TextField("Вътрешни бележки", blank=True)
    status = models.CharField(
        "Статус",
        max_length=16,
        choices=InquiryStatus.choices,
        default=InquiryStatus.NEW,
    )

    class Meta:
        db_table = "cms_inquirysubmission"
        ordering = ["-created_at", "-id"]
        verbose_name = "Запитване"
        verbose_name_plural = "Запитвания"

    def __str__(self):
        return f"{self.full_name} - {self.subject}"

    def get_admin_url(self):
        return reverse("admin:inquiries_inquirysubmission_change", args=[self.pk])
