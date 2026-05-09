from django.contrib import admin
from django.contrib.admin.utils import flatten_fieldsets
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.template.loader import render_to_string
from django.test import RequestFactory, TestCase

from inquiries.admin import InquirySubmissionAdmin
from inquiries.models import InquiryStatus, InquirySubmission, InquiryType

from .models import FooterLink, SiteSettings


class LegacyAdminRedirectTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_site_content")

    def test_legacy_cms_admin_root_redirects_to_admin_index(self):
        response = self.client.get("/admin/cms/", follow=False)

        self.assertRedirects(response, "/admin/", fetch_redirect_response=False)

    def test_legacy_staticpage_admin_redirects_to_pages_page(self):
        response = self.client.get("/admin/cms/staticpage/", follow=False)

        self.assertRedirects(response, "/admin/pages/page/", fetch_redirect_response=False)

    def test_legacy_inquiry_admin_redirects_to_inquiries_app(self):
        response = self.client.get("/admin/cms/inquirysubmission/", follow=False)

        self.assertRedirects(
            response,
            "/admin/inquiries/inquirysubmission/",
            fetch_redirect_response=False,
        )


class CoreModelConstraintTests(TestCase):
    def test_only_one_site_settings_record_is_allowed(self):
        SiteSettings.objects.create(site_name="Основен сайт")

        with self.assertRaises(ValidationError):
            SiteSettings(site_name="Втори сайт").full_clean()


class AdminCriticalBehaviorTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.bg",
            password="password123",
        )

    def test_site_settings_is_registered_in_admin_with_footer_contact_fields(self):
        self.assertTrue(admin.site.is_registered(SiteSettings))

        request = self.factory.get("/admin/core/sitesettings/")
        request.user = self.admin_user
        admin_instance = admin.site._registry[SiteSettings]
        fields = flatten_fieldsets(admin_instance.get_fieldsets(request))

        self.assertEqual(
            fields,
            [
                "address_line",
                "city",
                "postal_code",
                "phone_primary",
                "phone_secondary",
                "email",
                "working_hours_summary",
            ],
        )

        SiteSettings.objects.create()
        self.client.force_login(self.admin_user)
        response = self.client.get("/admin/core/sitesettings/1/change/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Контакти във футъра и контактната страница")
        self.assertContains(response, "field-address_line")
        self.assertContains(response, "field-city")
        self.assertContains(response, "field-postal_code")
        self.assertContains(response, "field-phone_primary")
        self.assertContains(response, "field-phone_secondary")
        self.assertContains(response, "field-email")
        self.assertContains(response, "field-working_hours_summary")
        self.assertNotContains(response, "Идентичност")
        self.assertNotContains(response, "Контактна страница")
        self.assertNotContains(response, "Карта и достъп")
        self.assertNotContains(response, "Правни текстове и бисквитки")
        self.assertNotContains(response, "field-site_name")
        self.assertNotContains(response, "field-contact_page_title")
        self.assertNotContains(response, "field-location_name")
        self.assertContains(response, 'value="Запис" class="default" name="_save"', html=False)
        self.assertNotContains(response, 'name="_continue"', html=False)
        self.assertNotContains(response, 'name="_addanother"', html=False)
        self.assertNotContains(response, 'class="deletelink"', html=False)

    def test_site_settings_admin_allows_only_one_record(self):
        request = self.factory.get("/admin/core/sitesettings/")
        request.user = self.admin_user
        admin_instance = admin.site._registry[SiteSettings]

        self.assertTrue(admin_instance.has_add_permission(request))
        SiteSettings.objects.create()
        self.assertFalse(admin_instance.has_add_permission(request))

    def test_footer_link_is_not_registered_in_admin(self):
        self.assertFalse(admin.site.is_registered(FooterLink))

    def test_inquiry_admin_actions_update_status(self):
        submission = InquirySubmission.objects.create(
            inquiry_type=InquiryType.GENERAL,
            full_name="Тест Потребител",
            email="user@example.bg",
            subject="Тестово запитване",
            message="Искам повече информация.",
        )
        request = self.factory.post("/admin/inquiries/inquirysubmission/")
        request.user = self.admin_user
        admin_instance = InquirySubmissionAdmin(InquirySubmission, admin.site)

        admin_instance.mark_reviewed(request, InquirySubmission.objects.filter(pk=submission.pk))
        submission.refresh_from_db()
        self.assertEqual(submission.status, InquiryStatus.REVIEWED)

        admin_instance.mark_closed(request, InquirySubmission.objects.filter(pk=submission.pk))
        submission.refresh_from_db()
        self.assertEqual(submission.status, InquiryStatus.CLOSED)

    def test_inquiry_admin_disallows_manual_add(self):
        request = self.factory.get("/admin/inquiries/inquirysubmission/")
        request.user = self.admin_user
        admin_instance = InquirySubmissionAdmin(InquirySubmission, admin.site)

        self.assertFalse(admin_instance.has_add_permission(request))

    def test_inquiry_changelist_hides_program_column(self):
        InquirySubmission.objects.create(
            inquiry_type=InquiryType.GENERAL,
            full_name="Тест Потребител",
            email="user@example.bg",
            subject="Тестово запитване",
            message="Искам повече информация.",
        )
        self.client.force_login(self.admin_user)

        response = self.client.get("/admin/inquiries/inquirysubmission/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "column-program")
        self.assertNotContains(response, ">Школа<", html=False)
        self.assertNotContains(response, '<div class="actions">', html=False)
        self.assertNotContains(response, "action-checkbox")
        self.assertNotContains(response, 'name="_selected_action"', html=False)

    def test_inquiry_change_form_hides_program_and_continue_action(self):
        submission = InquirySubmission.objects.create(
            inquiry_type=InquiryType.GENERAL,
            full_name="Тест Потребител",
            email="user@example.bg",
            subject="Тестово запитване",
            message="Искам повече информация.",
        )
        self.client.force_login(self.admin_user)

        response = self.client.get(f"/admin/inquiries/inquirysubmission/{submission.pk}/change/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="_continue"', html=False)
        self.assertNotContains(response, "field-program")
        self.assertNotContains(response, "Школа:")

    def test_auth_group_is_not_registered_in_admin(self):
        self.assertFalse(admin.site.is_registered(Group))

    def test_user_add_form_keeps_password_login_enabled(self):
        self.client.force_login(self.admin_user)

        response = self.client.get("/admin/auth/user/add/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "After you")
        self.assertNotContains(response, "usable_password")
        self.assertContains(response, 'value="Запис" class="default" name="_save"', html=False)
        self.assertNotContains(response, 'name="_continue"', html=False)
        self.assertNotContains(response, 'name="_addanother"', html=False)

        add_response = self.client.post(
            "/admin/auth/user/add/",
            {
                "username": "editor",
                "password1": "strong-password-123",
                "password2": "strong-password-123",
                "_save": "Запис",
            },
        )

        self.assertEqual(add_response.status_code, 302)
        self.assertTrue(get_user_model().objects.get(username="editor").has_usable_password())

    def test_user_change_form_only_edits_username_and_expected_actions(self):
        editor = get_user_model().objects.create_user(
            username="editor",
            email="editor@example.bg",
            password="strong-password-123",
        )
        self.client.force_login(self.admin_user)

        response = self.client.get(f"/admin/auth/user/{editor.pk}/change/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="username"', html=False)
        self.assertNotContains(response, 'id="id_password"', html=False)
        self.assertNotContains(response, "Лична информация")
        self.assertNotContains(response, "Права")
        self.assertNotContains(response, "Важни дати")
        self.assertNotContains(response, 'name="first_name"', html=False)
        self.assertNotContains(response, 'name="last_name"', html=False)
        self.assertNotContains(response, 'name="email"', html=False)
        self.assertNotContains(response, 'name="is_active"', html=False)
        self.assertNotContains(response, 'name="is_staff"', html=False)
        self.assertNotContains(response, 'name="is_superuser"', html=False)
        self.assertNotContains(response, 'name="groups"', html=False)
        self.assertNotContains(response, 'name="user_permissions"', html=False)
        self.assertNotContains(response, 'name="last_login_0"', html=False)
        self.assertNotContains(response, 'name="date_joined_0"', html=False)
        self.assertContains(response, 'value="Запис" class="default" name="_save"', html=False)
        self.assertContains(response, 'href="../password/">Възстановяване на парола</a>', html=False)
        self.assertContains(response, 'class="deletelink">Изтрий</a>', html=False)
        self.assertNotContains(response, 'name="_continue"', html=False)
        self.assertNotContains(response, 'name="_addanother"', html=False)

    def test_user_password_form_removes_password_login_toggle(self):
        editor = get_user_model().objects.create_user(
            username="editor",
            email="editor@example.bg",
            password="strong-password-123",
        )
        self.client.force_login(self.admin_user)

        response = self.client.get(f"/admin/auth/user/{editor.pk}/password/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="password1"', html=False)
        self.assertContains(response, 'name="password2"', html=False)
        self.assertNotContains(response, "usable_password")
        self.assertNotContains(response, "Влизане чрез парола")
        self.assertNotContains(response, "Изключено")
        self.assertNotContains(response, "Disable password-based authentication")

        post_response = self.client.post(
            f"/admin/auth/user/{editor.pk}/password/",
            {
                "password1": "strong-password-456",
                "password2": "strong-password-456",
                "set-password": "Change password",
            },
        )

        self.assertEqual(post_response.status_code, 302)
        editor.refresh_from_db()
        self.assertTrue(editor.check_password("strong-password-456"))
        self.assertTrue(editor.has_usable_password())

    def test_admin_app_list_omits_app_caption_links(self):
        request = self.factory.get("/admin/programs/program/")
        app_list = [
            {
                "app_label": "programs",
                "app_url": "/admin/programs/",
                "name": "Школи",
                "models": [
                    {
                        "object_name": "Program",
                        "admin_url": "/admin/programs/program/",
                        "add_url": "/admin/programs/program/add/",
                        "name": "Школи",
                        "view_only": False,
                    }
                ],
            }
        ]

        html = render_to_string(
            "admin/app_list.html",
            {"app_list": app_list, "show_changelinks": False},
            request=request,
        )

        self.assertNotIn("<caption", html)
        self.assertIn('aria-label="Школи"', html)
        self.assertIn('href="/admin/programs/program/"', html)

    def test_admin_home_renders_menu_only(self):
        self.client.force_login(self.admin_user)

        response = self.client.get("/admin/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "НЧ „Св. св. Кирил и Методий – 1926“")
        self.assertContains(response, 'id="nav-sidebar"', html=False)
        self.assertContains(response, 'id="nav-filter"', html=False)
        self.assertNotContains(response, "cc-admin-nav")
        self.assertNotContains(response, "cc-dashboard-hero")
        self.assertNotContains(response, "cc-dashboard-shortcuts")
        self.assertNotContains(response, "Последни действия")

    def test_admin_search_form_is_hidden(self):
        html = render_to_string("admin/search_form.html")

        self.assertNotIn("changelist-search", html)
        self.assertNotIn("searchbar", html)
