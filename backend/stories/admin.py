from django.contrib import admin

from core.admin_utils import SEO_FIELDSET, ZeroExtraTabularInline, build_image_preview

from .models import Story, StoryAttachment


class StoryAttachmentInline(ZeroExtraTabularInline):
    model = StoryAttachment


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ("cover_preview", "title", "story_type", "published_at", "is_featured", "is_published", "updated_at")
    list_filter = ("story_type", "is_published", "is_featured", "published_at")
    search_fields = ("title", "excerpt", "body", "seo_title", "seo_description")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    inlines = [StoryAttachmentInline]
    ordering = ("sort_order", "-published_at", "-id")
    readonly_fields = ("cover_preview",)
    fieldsets = (
        (
            "Основно",
            {
                "fields": (
                    "cover_preview",
                    "cover_image",
                    "story_type",
                    "title",
                    "slug",
                    "excerpt",
                    "body",
                    "published_at",
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
