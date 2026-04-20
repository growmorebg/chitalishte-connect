from django import forms
from django.contrib import admin
from django.db import models

from core.admin_utils import SEO_FIELDSET, ZeroExtraTabularInline, build_image_preview, publication_fieldset

from .models import BoardMember, GalleryImage, HistoryEntry, HomeFeature, HomeMetric, HomePage, LibraryImage, Page, PageType


class HomeMetricInline(ZeroExtraTabularInline):
    model = HomeMetric


class HomeFeatureInline(ZeroExtraTabularInline):
    model = HomeFeature


class PageAdminForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = "__all__"
        widgets = {
            "body": forms.Textarea(attrs={"rows": 18}),
            "intro": forms.Textarea(attrs={"rows": 4}),
            "callout_body": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        page_type = self.data.get(self.add_prefix("page_type")) or getattr(self.instance, "page_type", "")
        slug = self.data.get(self.add_prefix("slug")) or getattr(self.instance, "slug", "")
        html_enabled_slugs = {"history", "library"}
        is_html_enabled_page = page_type == PageType.HISTORY or slug in html_enabled_slugs
        if is_html_enabled_page:
            self.fields["body"].help_text = (
                "Тук може да поставяте обикновен текст или прост HTML като <h4>, <p>, <a> и списъци."
            )
            self.fields["body"].widget.attrs["rows"] = 24
        if slug == "library":
            self.fields["body"].label = "Описание"
            self.fields["body"].help_text = (
                "Основният текст за библиотеката. Може да използвате прост HTML като <p>, <h4>, <ul> и <a>."
            )
            self.fields["callout_title"].label = "Заглавие на секцията с работно време"
            self.fields["callout_body"].label = "Работно време"
            self.fields["callout_body"].help_text = "Въведете часовете по редове, например: Понеделник - петък: 09:00 - 18:00."
            self.fields["callout_body"].widget.attrs["rows"] = 8


class HistoryEntryAdminForm(forms.ModelForm):
    class Meta:
        model = HistoryEntry
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["title"].label = "Надпис"
        self.fields["title"].help_text = "По желание. Показва се под снимката."


class HistoryEntryInline(admin.StackedInline):
    form = HistoryEntryAdminForm
    model = HistoryEntry
    extra = 0
    fields = ("image", "preview", "title", "is_published", "sort_order")
    readonly_fields = ("preview",)
    verbose_name = "Снимка към историята"
    verbose_name_plural = "Снимки към историята"
    preview = build_image_preview("image")


class LibraryImageInline(admin.StackedInline):
    model = LibraryImage
    extra = 0
    fields = ("image", "preview", "caption", "is_published", "sort_order")
    readonly_fields = ("preview",)
    verbose_name = "Снимка към библиотеката"
    verbose_name_plural = "Снимки към библиотеката"
    preview = build_image_preview("image")


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm
    list_display = (
        "title",
        "page_type",
        "slug",
        "is_published",
        "show_in_header",
        "show_in_footer",
        "updated_at",
    )
    list_filter = ("page_type", "is_published", "show_in_header", "show_in_footer")
    search_fields = ("title", "navigation_title", "intro", "body", "seo_title", "seo_description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("sort_order", "title")
    fieldsets = (
        (
            "Основно",
            {
                "fields": (
                    "page_type",
                    "title",
                    "navigation_title",
                    "slug",
                    "intro",
                    "body",
                    "callout_title",
                    "callout_body",
                )
            },
        ),
        publication_fieldset("show_in_header", "show_in_footer"),
        SEO_FIELDSET,
    )

    formfield_overrides = {
        models.TextField: {"widget": forms.Textarea(attrs={"rows": 8})},
    }

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_inlines(self, request, obj):
        if obj and (obj.page_type == PageType.HISTORY or obj.slug == "history"):
            return [HistoryEntryInline]
        if obj and obj.slug == "library":
            return [LibraryImageInline]
        return []

    def get_fieldsets(self, request, obj=None):
        if obj and (obj.page_type == PageType.HISTORY or obj.slug == "history"):
            return (
                (
                    "Основно",
                    {
                        "description": (
                            "Страницата поддържа прост HTML в полето за съдържание. "
                            "Снимките се добавят от секцията под формата."
                        ),
                        "fields": (
                            "page_type",
                            "title",
                            "navigation_title",
                            "slug",
                            "intro",
                            "body",
                        ),
                    },
                ),
                publication_fieldset("show_in_header", "show_in_footer"),
                SEO_FIELDSET,
            )
        if obj and obj.slug == "library":
            return (
                (
                    "Основно",
                    {
                        "description": (
                            "Страницата има отделни публични секции за описание, работно време и снимки."
                        ),
                        "fields": (
                            "page_type",
                            "title",
                            "navigation_title",
                            "slug",
                            "intro",
                        ),
                    },
                ),
                (
                    "Описание",
                    {"fields": ("body",)},
                ),
                (
                    "Работно време",
                    {"fields": ("callout_title", "callout_body")},
                ),
                publication_fieldset("show_in_header", "show_in_footer"),
                SEO_FIELDSET,
            )
        return super().get_fieldsets(request, obj)


@admin.register(BoardMember)
class BoardMemberAdmin(admin.ModelAdmin):
    list_display = ("portrait_preview", "full_name", "role", "phone", "is_published", "sort_order", "updated_at")
    list_filter = ("is_published",)
    search_fields = ("full_name", "role", "short_bio", "biography", "email", "phone")
    prepopulated_fields = {"slug": ("full_name",)}
    ordering = ("sort_order", "full_name")
    readonly_fields = ("portrait_preview",)
    fieldsets = (
        (
            "Основно",
            {
                "fields": (
                    "portrait_preview",
                    "portrait",
                    "full_name",
                    "slug",
                    "role",
                    "phone",
                    "email",
                )
            },
        ),
        (
            "Съдържание",
            {"fields": ("short_bio", "biography")},
        ),
        publication_fieldset(),
    )
    portrait_preview = build_image_preview("portrait", description="Портрет", width=72, height=72)


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("thumbnail", "caption", "alt_text", "is_published", "sort_order", "created_at")
    list_filter = ("is_published",)
    search_fields = ("caption", "alt_text")
    ordering = ("sort_order", "id")
    readonly_fields = ("thumbnail",)
    fieldsets = (
        (
            "Изображение",
            {"fields": ("thumbnail", "image", "caption", "alt_text")},
        ),
        publication_fieldset(),
    )
    thumbnail = build_image_preview("image")
