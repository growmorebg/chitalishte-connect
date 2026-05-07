from pathlib import Path

from django import forms
from django.contrib import admin, messages
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.template.response import TemplateResponse
from django.urls import path, reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils.html import format_html
from django.utils.text import slugify

from core.admin_utils import ZeroExtraTabularInline, build_image_preview

from .models import Story, StoryAttachment


class StoryAttachmentInlineForm(forms.ModelForm):
    class Meta:
        model = StoryAttachment
        fields = "__all__"
        widgets = {
            "file": forms.FileInput(attrs={"class": "cc-story-attachment-file-input"}),
        }


class StoryAttachmentInline(ZeroExtraTabularInline):
    model = StoryAttachment
    form = StoryAttachmentInlineForm
    fields = ("sort_order", "image_preview", "file")
    readonly_fields = ("image_preview",)
    verbose_name = "Снимка към публикация"
    verbose_name_plural = "Снимки към публикации"

    class Media:
        js = ("cms/js/admin_story_attachments.js",)

    @admin.display(description="Снимка")
    def image_preview(self, obj):
        if not obj or not obj.is_image:
            return "—"

        try:
            image_url = obj.file.url
        except (AttributeError, ValueError):
            return "—"

        return format_html(
            '<img class="story-attachment-preview" src="{}" '
            'style="width:120px;height:80px;object-fit:cover;border-radius:8px;" alt="">',
            image_url,
        )


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    change_form_template = "admin/stories/story/change_form.html"
    list_display = (
        "cover_preview",
        "title",
        "story_type",
        "published_at",
        "is_featured",
        "is_published",
        "preview_link",
        "updated_at",
    )
    list_filter = ("story_type", "is_published", "is_featured", "published_at")
    search_fields = ("title", "excerpt", "body")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    inlines = [StoryAttachmentInline]
    ordering = ("sort_order", "-published_at", "-id")
    readonly_fields = ("cover_preview", "preview_link")
    editor_fieldsets = (
        (
            "Основно",
            {
                "fields": (
                    "cover_image",
                    "story_type",
                    "title",
                    "body",
                    "published_at",
                )
            },
        ),
        (
            "Публикация",
            {"fields": ("is_featured", "sort_order")},
        ),
    )
    add_fieldsets = editor_fieldsets
    fieldsets = editor_fieldsets
    cover_preview = build_image_preview("cover_image")

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_prepopulated_fields(self, request, obj=None):
        return {}

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<path:object_id>/preview/",
                self.admin_site.admin_view(self.preview_view),
                name="stories_story_preview",
            ),
            path(
                "<path:object_id>/toggle-publish/",
                self.admin_site.admin_view(self.toggle_publish_view),
                name="stories_story_toggle_publish",
            ),
        ]
        return custom_urls + urls

    def get_list_display(self, request):
        return (
            "cover_preview",
            "title",
            "story_type",
            "published_at",
            "is_featured",
            "is_published",
            self.build_publish_toggle(request),
            "preview_link",
            "updated_at",
        )

    def build_publish_toggle(self, request):
        @admin.display(description="Статус")
        def publish_toggle(obj):
            if not obj.pk:
                return "—"

            label = "Скрий" if obj.is_published else "Публикувай"
            action_class = "cc-row-action--unpublish" if obj.is_published else "cc-row-action--publish"
            return format_html(
                '<button class="cc-row-action {}" type="submit" name="_toggle_publish" value="{}" formnovalidate>{}</button>',
                action_class,
                obj.pk,
                label,
            )

        return publish_toggle

    def changelist_view(self, request, extra_context=None):
        if request.method == "POST" and "_toggle_publish" in request.POST:
            return self.toggle_publish(request, request.POST["_toggle_publish"], request.get_full_path())
        return super().changelist_view(request, extra_context)

    def get_view_on_site_url(self, obj=None):
        if obj is None or not obj.pk:
            return None
        return reverse("admin:stories_story_preview", args=(obj.pk,))

    @admin.display(description="Преглед")
    def preview_link(self, obj):
        if not obj.pk:
            return "Запазете публикацията, за да видите преглед."
        return format_html(
            '<a class="cc-row-action cc-row-action--preview" href="{}" target="_blank" rel="noopener">Преглед</a>',
            self.get_view_on_site_url(obj),
        )

    def preview_view(self, request, object_id):
        story = self.get_object(request, object_id)
        if story is None:
            raise Http404("Публикацията не е намерена.")
        if not self.has_view_or_change_permission(request, story):
            raise PermissionDenied

        response = TemplateResponse(
            request,
            "cms/project_detail.html",
            {
                "project": story,
                "related_projects": [],
                "is_preview": True,
            },
        )
        response["X-Robots-Tag"] = "noindex, nofollow"
        return response

    def toggle_publish_view(self, request, object_id):
        story = self.get_object(request, object_id)
        if story is None:
            raise Http404("Публикацията не е намерена.")
        if not self.has_change_permission(request, story):
            raise PermissionDenied
        if request.method != "POST":
            return HttpResponseRedirect(self.get_changelist_url())

        next_url = request.POST.get("next") or self.get_changelist_url()
        if not url_has_allowed_host_and_scheme(
            next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = self.get_changelist_url()
        return self.toggle_publish(request, object_id, next_url)

    def toggle_publish(self, request, object_id, next_url):
        story = self.get_object(request, object_id)
        if story is None:
            raise Http404("Публикацията не е намерена.")
        if not self.has_change_permission(request, story):
            raise PermissionDenied

        story.is_published = not story.is_published
        story.save(update_fields=["is_published", "updated_at"])
        messages.success(
            request,
            f"Публикацията „{story.title}“ е {'публикувана' if story.is_published else 'скрита'}.",
        )

        return HttpResponseRedirect(next_url)

    def get_changelist_url(self):
        return reverse("admin:stories_story_changelist")

    def generate_unique_slug(self, title):
        base_slug = slugify(title) or "publication"
        slug = base_slug
        index = 2

        while Story.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{index}"
            index += 1

        return slug

    def generate_excerpt(self, story):
        summary = " ".join(story.body.split())
        return summary[:220] if summary else story.title

    def save_model(self, request, obj, form, change):
        if not change:
            obj.is_published = False
            obj.slug = obj.slug or self.generate_unique_slug(obj.title)
            obj.excerpt = obj.excerpt or self.generate_excerpt(obj)

        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for deleted_obj in formset.deleted_objects:
            deleted_obj.delete()

        for instance in instances:
            if isinstance(instance, StoryAttachment) and not instance.title and instance.file:
                instance.title = Path(instance.file.name).name
            instance.save()

        formset.save_m2m()
