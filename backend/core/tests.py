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

        self.assertIn("address_line", fields)
        self.assertIn("city", fields)
        self.assertIn("phone_primary", fields)
        self.assertIn("email", fields)
        self.assertIn("working_hours_summary", fields)
        self.assertIn("contact_page_title", fields)
        self.assertIn("contact_page_intro", fields)
        self.assertIn("contact_page_map_label", fields)
        self.assertIn("contact_page_form_heading", fields)
        self.assertIn("contact_page_submit_label", fields)
        self.assertIn("contact_page_privacy_note", fields)

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

    def test_auth_group_is_not_registered_in_admin(self):
        self.assertFalse(admin.site.is_registered(Group))

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
