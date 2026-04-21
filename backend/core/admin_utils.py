from django.contrib import admin
from django.utils.html import format_html


class SingletonAdmin(admin.ModelAdmin):
    save_on_top = True

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


class ZeroExtraTabularInline(admin.TabularInline):
    extra = 0


SEO_FIELDSET = ("SEO", {"fields": ("seo_title", "seo_description", "seo_image")})


def publication_fieldset(*fields):
    return ("Публикация", {"fields": (*fields, "is_published", "sort_order")})


def image_preview(obj, field_name, *, width=120, height=80):
    image = getattr(obj, field_name, None)
    if not image:
        return "—"

    try:
        url = image.url
    except (AttributeError, ValueError):
        return "—"

    return format_html(
        '<img src="{}" style="width:{}px;height:{}px;object-fit:cover;border-radius:8px;" alt="">',
        url,
        width,
        height,
    )


def build_image_preview(field_name, *, description="Преглед", width=120, height=80):
    @admin.display(description=description)
    def preview(_self, obj):
        return image_preview(obj, field_name, width=width, height=height)

    return preview
