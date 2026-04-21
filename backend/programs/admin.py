from django.contrib import admin

from core.admin_utils import (
    SEO_FIELDSET,
    ZeroExtraTabularInline,
    build_image_preview,
)

from .models import (
    Instructor,
    PricingBlock,
    Program,
    ProgramGalleryImage,
    ProgramSchedule,
)


class ProgramScheduleInline(ZeroExtraTabularInline):
    model = ProgramSchedule


class PricingBlockInline(ZeroExtraTabularInline):
    model = PricingBlock


class ProgramGalleryImageInline(ZeroExtraTabularInline):
    model = ProgramGalleryImage
    readonly_fields = ("thumbnail",)
    fields = ("thumbnail", "image", "caption", "sort_order")
    thumbnail = build_image_preview("image", width=96, height=64)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ("portrait_preview", "full_name", "role_title", "is_published", "sort_order", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("full_name", "role_title", "biography", "credentials")
    prepopulated_fields = {"slug": ("full_name",)}
    ordering = ("sort_order", "full_name")
    readonly_fields = ("portrait_preview",)
    portrait_preview = build_image_preview("portrait", description="Портрет", width=72, height=72)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = (
        "cover_preview",
        "title",
        "category",
        "inquiry_phone",
        "is_featured",
        "is_published",
        "sort_order",
        "updated_at",
    )
    list_filter = ("is_published", "is_featured", "category")
    search_fields = ("title", "summary", "description", "audience", "age_group", "level", "inquiry_phone")
    filter_horizontal = ("instructors",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProgramScheduleInline, PricingBlockInline, ProgramGalleryImageInline]
    ordering = ("sort_order", "title")
    readonly_fields = ("cover_preview",)
    fieldsets = (
        (
            "Основно",
            {
                "fields": (
                    "cover_preview",
                    "cover_image",
                    "category",
                    "title",
                    "slug",
                    "summary",
                    "description",
                    "instructors",
                )
            },
        ),
        (
            "Детайли за участие",
            {
                "fields": (
                    "audience",
                    "age_group",
                    "level",
                    "duration",
                    "location_name",
                    "inquiry_phone",
                )
            },
        ),
        (
            "Публикация",
            {"fields": ("is_featured", "is_published", "sort_order")},
        ),
        SEO_FIELDSET,
    )
    cover_preview = build_image_preview("cover_image")
