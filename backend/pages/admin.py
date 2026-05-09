from django import forms
from django.contrib import admin
from django.db import models
from django.utils.text import slugify

from core.admin_utils import ZeroExtraTabularInline, build_image_preview, publication_fieldset

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


class BoardMemberAdminForm(forms.ModelForm):
    class Meta:
        model = BoardMember
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["short_bio"].label = "Биография"


class HistoryEntryInline(admin.StackedInline):
    form = HistoryEntryAdminForm
    model = HistoryEntry
    template = "admin/pages/page/edit_inline/image_stacked.html"
    extra = 0
    fields = ("image", "title")
    verbose_name = "Снимка към историята"
    verbose_name_plural = "Снимки към историята"

    class Media:
        js = ("cms/js/admin_story_attachments.js",)


class LibraryImageInline(admin.StackedInline):
    model = LibraryImage
    template = "admin/pages/page/edit_inline/image_stacked.html"
    extra = 0
    fields = ("image", "caption")
    verbose_name = "Снимка към библиотеката"
    verbose_name_plural = "Снимки към библиотеката"

    class Media:
        js = ("cms/js/admin_story_attachments.js",)


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    form = PageAdminForm
    list_display = (
        "title",
        "updated_at",
    )
    list_filter = ()
    search_fields = ("title", "navigation_title", "intro", "body")
    prepopulated_fields = {}
    ordering = ("sort_order", "title")
    fieldsets = (
        (
            "Основно",
            {
                "fields": (
                    "body",
                    "callout_title",
                    "callout_body",
                )
            },
        ),
        publication_fieldset("show_in_header", "show_in_footer"),
    )

    formfield_overrides = {
        models.TextField: {"widget": forms.Textarea(attrs={"rows": 8})},
    }

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        resolver_match = getattr(request, "resolver_match", None)
        if resolver_match and resolver_match.url_name == "pages_page_changelist":
            return queryset.exclude(slug__in=("board", "privacy", "cookies"))
        return queryset

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
                        "fields": ("body",),
                    },
                ),
            )
        if obj and obj.slug == "library":
            return (
                (
                    "Описание",
                    {"fields": ("body",)},
                ),
                (
                    "Работно време",
                    {"fields": ("callout_title", "callout_body")},
                ),
            )
        if obj and (obj.page_type == PageType.CHARTER or obj.slug == "charter"):
            return (
                (
                    "Основно",
                    {"fields": ("body",)},
                ),
            )
        return super().get_fieldsets(request, obj)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = {
            **(extra_context or {}),
            "show_save_and_continue": False,
            "show_save_and_add_another": False,
        }
        return super().changeform_view(request, object_id, form_url, extra_context)


@admin.register(BoardMember)
class BoardMemberAdmin(admin.ModelAdmin):
    form = BoardMemberAdminForm
    change_form_template = "admin/pages/boardmember/change_form.html"
    list_display = ("portrait_preview", "full_name", "role", "phone", "updated_at")
    list_filter = ()
    search_fields = ("full_name", "role", "short_bio", "biography", "email", "phone")
    prepopulated_fields = {}
    ordering = ("full_name",)
    fieldsets = (
        (
            "Основно",
            {
                "fields": (
                    "portrait",
                    "full_name",
                    "role",
                    "phone",
                    "email",
                )
            },
        ),
        (
            "Съдържание",
            {"fields": ("short_bio",)},
        ),
    )
    portrait_preview = build_image_preview("portrait", description="Портрет", width=72, height=72)

    def _generate_unique_slug(self, obj):
        max_length = BoardMember._meta.get_field("slug").max_length
        base_slug = slugify(obj.full_name, allow_unicode=True) or "board-member"
        base_slug = base_slug[:max_length]
        slug = base_slug
        suffix = 2
        queryset = BoardMember.objects.exclude(pk=obj.pk)

        while queryset.filter(slug=slug).exists():
            suffix_text = f"-{suffix}"
            slug = f"{base_slug[: max_length - len(suffix_text)]}{suffix_text}"
            suffix += 1

        return slug

    def save_model(self, request, obj, form, change):
        if not obj.slug:
            obj.slug = self._generate_unique_slug(obj)
        if not change:
            obj.is_published = True
        super().save_model(request, obj, form, change)


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    change_form_template = "admin/pages/galleryimage/change_form.html"
    list_display = ("thumbnail", "caption", "alt_text", "is_published", "sort_order", "created_at")
    list_filter = ("is_published",)
    search_fields = ("caption", "alt_text")
    ordering = ("sort_order", "id")
    readonly_fields = ("thumbnail",)
    fieldsets = (
        (
            "Изображение",
            {"fields": ("thumbnail", "image", "caption")},
        ),
        publication_fieldset(),
    )
    thumbnail = build_image_preview("image")
