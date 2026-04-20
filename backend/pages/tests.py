from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .admin import HistoryEntryInline, LibraryImageInline, PageAdmin
from .models import HistoryEntry, HomePage, LibraryImage, Page, PageType


class PageModelTests(TestCase):
    def test_page_manager_published_returns_only_published_records(self):
        visible = Page.objects.create(title="Видима страница", slug="visible-page", body="Текст")
        Page.objects.create(
            title="Скрита страница",
            slug="hidden-page",
            body="Текст",
            is_published=False,
        )

        self.assertQuerySetEqual(
            Page.objects.published().filter(slug__in=["visible-page", "hidden-page"]),
            [visible],
            transform=lambda item: item,
        )

    def test_special_page_urls_resolve_to_named_routes(self):
        history = Page(title="История", slug="history", body="Текст")
        library = Page(title="Библиотека", slug="library", body="Текст")
        board = Page(title="Настоятелство", slug="board", body="Текст")
        privacy = Page(title="Поверителност", slug="privacy", body="Текст", page_type=PageType.PRIVACY)
        cookies = Page(title="Бисквитки", slug="cookies", body="Текст", page_type=PageType.COOKIES)
        standard = Page(title="Правила", slug="rules", body="Текст")

        self.assertEqual(history.get_absolute_url(), reverse("cms:history"))
        self.assertEqual(library.get_absolute_url(), reverse("cms:library"))
        self.assertEqual(board.get_absolute_url(), reverse("cms:board"))
        self.assertEqual(privacy.get_absolute_url(), reverse("cms:privacy"))
        self.assertEqual(cookies.get_absolute_url(), reverse("cms:cookies"))
        self.assertEqual(standard.get_absolute_url(), reverse("cms:page_detail", kwargs={"slug": "rules"}))

    def test_page_knows_when_it_is_legal_content(self):
        legal_page = Page(title="Поверителност", slug="privacy", body="Текст", page_type=PageType.PRIVACY)
        non_legal_page = Page(title="Екип", slug="team", body="Текст", page_type=PageType.STANDARD)

        self.assertTrue(legal_page.is_legal_page)
        self.assertFalse(non_legal_page.is_legal_page)


class HistoryEntryModelTests(TestCase):
    def setUp(self):
        self.page = Page.objects.create(
            title="История",
            navigation_title="История",
            slug="history",
            body="Текст",
            page_type=PageType.HISTORY,
        )

    def test_history_entry_generates_slug_when_missing(self):
        entry = HistoryEntry.objects.create(page=self.page, title="Founding")

        self.assertEqual(entry.slug, "founding")

    def test_history_entry_generates_unique_slug_when_reused(self):
        HistoryEntry.objects.create(page=self.page, title="Founding")
        entry = HistoryEntry.objects.create(page=self.page, title="Founding")

        self.assertEqual(entry.slug, "founding-2")


class PageAdminTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.bg",
            password="password123",
        )
        self.history_page = Page.objects.create(
            title="История",
            navigation_title="История",
            slug="history",
            body="Текст",
            page_type=PageType.HISTORY,
        )
        self.standard_page = Page.objects.create(
            title="Правила",
            navigation_title="Правила",
            slug="rules",
            body="Текст",
        )
        self.library_page, _ = Page.objects.update_or_create(
            slug="library",
            defaults={
                "title": "Библиотека",
                "navigation_title": "Библиотека",
                "body": "Описание",
            },
        )

    def test_page_admin_disables_add_and_delete_permissions(self):
        request = self.factory.get("/admin/pages/page/")
        request.user = self.admin_user
        admin_instance = PageAdmin(Page, AdminSite())

        self.assertFalse(admin_instance.has_add_permission(request))
        self.assertFalse(admin_instance.has_delete_permission(request, self.standard_page))

    def test_page_admin_changelist_hides_add_button(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:pages_page_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, reverse("admin:pages_page_add"))

    def test_page_admin_add_view_is_blocked(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:pages_page_add"))

        self.assertEqual(response.status_code, 403)

    def test_page_admin_allows_editing_existing_pages(self):
        self.client.force_login(self.admin_user)
        change_url = reverse("admin:pages_page_change", args=[self.standard_page.pk])

        response = self.client.post(
            change_url,
            data={
                "page_type": PageType.STANDARD,
                "title": "Обновени правила",
                "navigation_title": "Правила",
                "slug": "rules",
                "intro": "Нов увод",
                "body": "Обновено съдържание",
                "callout_title": "Важно",
                "callout_body": "Подробности",
                "show_in_header": "on",
                "show_in_footer": "on",
                "is_published": "on",
                "sort_order": 5,
                "seo_title": "SEO правила",
                "seo_description": "SEO описание",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.standard_page.refresh_from_db()
        self.assertEqual(self.standard_page.title, "Обновени правила")
        self.assertEqual(self.standard_page.body, "Обновено съдържание")
        self.assertEqual(self.standard_page.sort_order, 5)
        self.assertTrue(self.standard_page.show_in_header)
        self.assertTrue(self.standard_page.show_in_footer)

    def test_history_page_admin_shows_image_inline(self):
        request = RequestFactory().get("/admin/pages/page/1/change/")
        request.user = self.admin_user
        admin_instance = PageAdmin(Page, AdminSite())

        self.assertEqual(admin_instance.get_inlines(request, self.history_page), [HistoryEntryInline])
        self.assertEqual(admin_instance.get_inlines(request, self.standard_page), [])

    def test_library_page_admin_shows_library_image_inline(self):
        request = RequestFactory().get("/admin/pages/page/1/change/")
        request.user = self.admin_user
        admin_instance = PageAdmin(Page, AdminSite())

        self.assertEqual(admin_instance.get_inlines(request, self.library_page), [LibraryImageInline])

    def test_history_entry_is_only_available_as_page_inline(self):
        self.assertFalse(admin.site.is_registered(HistoryEntry))

    def test_library_image_is_only_available_as_page_inline(self):
        self.assertFalse(admin.site.is_registered(LibraryImage))

    def test_homepage_is_not_registered_in_admin(self):
        self.assertFalse(admin.site.is_registered(HomePage))
