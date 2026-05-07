from django.contrib import admin
from django.utils.text import slugify

from core.admin_utils import (
    ZeroExtraTabularInline,
    build_image_preview,
)

from .models import (
    Instructor,
    PricingBlock,
    Program,
    ProgramCategory,
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


@admin.register(ProgramCategory)
class ProgramCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_published", "sort_order")
    list_filter = ("is_published",)
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")
    add_fieldsets = (
        (
            "Основно",
            {
                "fields": (
                    "name",
                    "description",
                )
            },
        ),
        (
            "Публикация",
            {"fields": ("is_published", "sort_order")},
        ),
    )
    fieldsets = (
        (
            "Основно",
            {
                "fields": (
                    "name",
                    "slug",
                    "description",
                )
            },
        ),
        (
            "Публикация",
            {"fields": ("is_published", "sort_order")},
        ),
    )

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_prepopulated_fields(self, request, obj=None):
        if obj is None:
            return {}
        return super().get_prepopulated_fields(request, obj)

    def generate_unique_slug(self, name):
        base_slug = slugify(name) or "program-category"
        slug = base_slug
        index = 2

        while ProgramCategory.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{index}"
            index += 1

        return slug

    def save_model(self, request, obj, form, change):
        if not change:
            obj.slug = obj.slug or self.generate_unique_slug(obj.name)

        super().save_model(request, obj, form, change)


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
    )
    cover_preview = build_image_preview("cover_image")
