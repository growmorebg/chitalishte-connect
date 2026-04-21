from django.contrib import admin
from django.utils import timezone

from .models import InquiryStatus, InquirySubmission


@admin.register(InquirySubmission)
class InquirySubmissionAdmin(admin.ModelAdmin):
    list_display = ("full_name", "subject", "inquiry_type", "status", "program", "created_at")
    list_filter = ("inquiry_type", "status", "created_at")
    search_fields = ("full_name", "email", "subject", "message", "admin_notes")
    autocomplete_fields = ("program",)
    list_select_related = ("program",)
    date_hierarchy = "created_at"
    actions = ("mark_new", "mark_reviewed", "mark_closed")
    readonly_fields = (
        "inquiry_type",
        "program",
        "full_name",
        "email",
        "phone",
        "subject",
        "message",
        "created_at",
        "updated_at",
    )
    fieldsets = (
        (
            "Детайли",
            {
                "fields": (
                    "inquiry_type",
                    "program",
                    "full_name",
                    "email",
                    "phone",
                    "subject",
                    "message",
                )
            },
        ),
        (
            "Обработка",
            {"fields": ("status", "admin_notes", "created_at", "updated_at")},
        ),
    )

    def has_add_permission(self, request):
        return False

    @admin.action(description="Маркирай като ново")
    def mark_new(self, request, queryset):
        queryset.update(status=InquiryStatus.NEW, updated_at=timezone.now())

    @admin.action(description="Маркирай като прегледано")
    def mark_reviewed(self, request, queryset):
        queryset.update(status=InquiryStatus.REVIEWED, updated_at=timezone.now())

    @admin.action(description="Маркирай като приключено")
    def mark_closed(self, request, queryset):
        queryset.update(status=InquiryStatus.CLOSED, updated_at=timezone.now())
