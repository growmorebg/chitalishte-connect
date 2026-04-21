from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.models import Group

from .models import SiteSettings


admin.site.site_header = "НЧ „Св. св. Кирил и Методий – 1926“"
admin.site.site_title = "Администрация"
admin.site.index_title = "Управление на съдържанието"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ("site_name", "phone_primary", "email", "city", "updated_at")
    fieldsets = (
        (
            "Идентичност",
            {
                "fields": (
                    "site_name",
                    "site_tagline",
                    "footer_summary",
                )
            },
        ),
        (
            "Контакти във футъра и контактната страница",
            {
                "fields": (
                    "address_line",
                    "city",
                    "postal_code",
                    "phone_primary",
                    "phone_secondary",
                    "email",
                    "working_hours_summary",
                )
            },
        ),
        (
            "Контактна страница",
            {
                "fields": (
                    "contact_page_title",
                    "contact_page_intro",
                    "contact_page_hours_label",
                    "contact_page_map_label",
                    "contact_page_form_heading",
                    "contact_page_submit_label",
                    "contact_page_privacy_note",
                    "contact_page_success_message",
                )
            },
        ),
        (
            "Карта и достъп",
            {
                "fields": (
                    "location_name",
                    "location_short_description",
                    "map_embed_url",
                    "location_access_notes",
                )
            },
        ),
        (
            "Правни текстове и бисквитки",
            {
                "fields": (
                    "copyright_notice",
                    "cookie_banner_title",
                    "cookie_banner_text",
                )
            },
        ),
        (
            "SEO",
            {
                "classes": ("collapse",),
                "fields": (
                    "seo_title",
                    "seo_description",
                    "seo_image",
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


try:
    admin.site.unregister(Group)
except NotRegistered:
    pass
