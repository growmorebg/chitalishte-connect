from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import AdminPasswordChangeForm, UserCreationForm
from django.contrib.auth.models import Group, User

from .models import SiteSettings


admin.site.site_header = "НЧ „Св. св. Кирил и Методий – 1926“"
admin.site.site_title = "Администрация"
admin.site.index_title = "Управление на съдържанието"
admin.site.disable_action("delete_selected")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    change_form_template = "admin/core/sitesettings/change_form.html"
    list_display = ("site_name", "phone_primary", "email", "city", "updated_at")
    fieldsets = (
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
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


try:
    admin.site.unregister(Group)
except NotRegistered:
    pass


try:
    admin.site.unregister(User)
except NotRegistered:
    pass


class AdminPasswordResetForm(AdminPasswordChangeForm):
    def __init__(self, user, *args, **kwargs):
        super().__init__(user, *args, **kwargs)
        self.fields.pop("usable_password", None)
        self.fields["password1"].required = True
        self.fields["password2"].required = True


@admin.register(User)
class ChitalishteUserAdmin(UserAdmin):
    list_display = ("username",)
    list_filter = ()
    fieldsets = ((None, {"fields": ("username",)}),)
    add_form = UserCreationForm
    change_password_form = AdminPasswordResetForm
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2"),
            },
        ),
    )
