from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .admin import HistoryEntryInline, LibraryImageInline, PageAdmin
from .models import BoardMember, GalleryImage, HistoryEntry, HomePage, LibraryImage, Page, PageType


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
        self.charter_page = Page.objects.create(
            title="Устав",
            navigation_title="Устав",
            slug="charter",
            body="Текст",
            page_type=PageType.CHARTER,
        )
        self.board_page = Page.objects.create(
            title="Настоятелство и екип",
            navigation_title="Настоятелство",
            slug="board",
            body="Текст",
            page_type=PageType.GOVERNANCE,
            show_in_header=True,
        )
        self.privacy_page = Page.objects.create(
            title="Политика за поверителност",
            slug="privacy",
            body="Текст",
            page_type=PageType.PRIVACY,
        )
        self.cookies_page = Page.objects.create(
            title="Политика за бисквитки",
            slug="cookies",
            body="Текст",
            page_type=PageType.COOKIES,
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

    def test_page_admin_menu_link_is_renamed_to_about_us(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<a href="/admin/pages/page/">За Нас</a>', html=False)
        self.assertNotContains(response, '<a href="/admin/pages/page/">Страници</a>', html=False)

    def test_page_admin_changelist_hides_hidden_pages(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:pages_page_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.standard_page.title)
        self.assertNotContains(response, reverse("admin:pages_page_change", args=[self.board_page.pk]))
        self.assertNotContains(response, reverse("admin:pages_page_change", args=[self.privacy_page.pk]))
        self.assertNotContains(response, reverse("admin:pages_page_change", args=[self.cookies_page.pk]))
        self.assertNotContains(response, '<td class="field-slug">board</td>', html=True)
        self.assertNotContains(response, "Политика за поверителност")
        self.assertNotContains(response, "Политика за бисквитки")
        self.assertNotContains(response, "?page_type=governance")

    def test_page_admin_changelist_uses_minimal_columns(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:pages_page_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "column-title")
        self.assertContains(response, "column-updated_at")
        self.assertNotContains(response, "column-page_type")
        self.assertNotContains(response, "column-slug")
        self.assertNotContains(response, "column-is_published")
        self.assertNotContains(response, "column-show_in_header")
        self.assertNotContains(response, "column-show_in_footer")

    def test_page_admin_changelist_has_no_filter_sidebar(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:pages_page_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="changelist-filter"')

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
        self.assertEqual(self.standard_page.title, "Правила")
        self.assertEqual(self.standard_page.body, "Обновено съдържание")
        self.assertEqual(self.standard_page.sort_order, 5)
        self.assertTrue(self.standard_page.show_in_header)
        self.assertTrue(self.standard_page.show_in_footer)

    def test_history_page_admin_change_form_hides_page_metadata_and_publication_controls(self):
        HistoryEntry.objects.create(page=self.history_page, title="Стара снимка")
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:pages_page_change", args=[self.history_page.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "field-body")
        self.assertContains(response, "history_entries-group")
        self.assertNotContains(response, 'id="id_page_type"')
        self.assertNotContains(response, 'id="id_title"')
        self.assertNotContains(response, 'id="id_navigation_title"')
        self.assertNotContains(response, 'id="id_slug"')
        self.assertNotContains(response, 'id="id_intro"')
        self.assertNotContains(response, "fieldset-heading\">Публикация")
        self.assertNotContains(response, 'id="id_show_in_header"')
        self.assertNotContains(response, 'id="id_show_in_footer"')
        self.assertNotContains(response, 'id="id_is_published"')
        self.assertNotContains(response, 'id="id_sort_order"')
        self.assertContains(response, 'id="id_history_entries-0-image"', html=False)
        self.assertContains(response, 'id="id_history_entries-0-title"', html=False)
        self.assertNotContains(response, "field-preview")
        self.assertNotContains(response, 'id="id_history_entries-0-is_published"', html=False)
        self.assertNotContains(response, 'id="id_history_entries-0-sort_order"', html=False)
        self.assertNotContains(response, '<h3><b>Снимка към историята:</b>', html=False)
        self.assertNotContains(response, "inline_label")
        self.assertNotContains(response, 'class="vCheckboxLabel inline"', html=False)
        self.assertContains(response, 'name="history_entries-0-DELETE"', html=False)
        self.assertContains(response, 'class="cc-inline-delete-button"', html=False)
        self.assertContains(response, "cc-page-image-inline__delete")
        self.assertContains(response, '<path d="M3 6h18"></path>', html=False)
        self.assertContains(response, 'name="_save"')
        self.assertNotContains(response, 'name="_continue"')

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

    def test_library_page_admin_change_form_hides_intro_and_minimizes_image_inline(self):
        LibraryImage.objects.create(page=self.library_page, image="library/example.jpg", caption="Фонд")
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:pages_page_change", args=[self.library_page.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="id_intro"')
        self.assertNotContains(response, "Страницата има отделни публични секции за описание")
        self.assertContains(response, "field-body")
        self.assertContains(response, "field-callout_title")
        self.assertContains(response, "field-callout_body")
        self.assertContains(response, "library_images-group")
        self.assertContains(response, 'id="id_library_images-0-image"', html=False)
        self.assertContains(response, 'id="id_library_images-0-caption"', html=False)
        self.assertNotContains(response, "field-preview")
        self.assertNotContains(response, 'id="id_library_images-0-is_published"', html=False)
        self.assertNotContains(response, 'id="id_library_images-0-sort_order"', html=False)
        self.assertContains(response, 'name="library_images-0-DELETE"', html=False)
        self.assertContains(response, 'class="cc-inline-delete-button"', html=False)
        self.assertContains(response, "cc-page-image-inline__delete")

    def test_charter_page_admin_change_form_hides_callout_and_publication_controls(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:pages_page_change", args=[self.charter_page.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "field-body")
        self.assertNotContains(response, "field-callout_title")
        self.assertNotContains(response, "field-callout_body")
        self.assertNotContains(response, 'id="id_callout_title"')
        self.assertNotContains(response, 'id="id_callout_body"')
        self.assertNotContains(response, "fieldset-heading\">Публикация")
        self.assertNotContains(response, 'id="id_show_in_header"')
        self.assertNotContains(response, 'id="id_show_in_footer"')
        self.assertNotContains(response, 'id="id_is_published"')
        self.assertNotContains(response, 'id="id_sort_order"')

    def test_history_entry_is_only_available_as_page_inline(self):
        self.assertFalse(admin.site.is_registered(HistoryEntry))

    def test_library_image_is_only_available_as_page_inline(self):
        self.assertFalse(admin.site.is_registered(LibraryImage))

    def test_homepage_is_not_registered_in_admin(self):
        self.assertFalse(admin.site.is_registered(HomePage))

    def test_gallery_image_change_form_hides_alt_text_and_limits_actions(self):
        gallery_image = GalleryImage.objects.create(
            image="gallery/example.jpg",
            caption="Снимка от събитие",
            alt_text="Описание за скрийнрийдър",
        )
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:pages_galleryimage_change", args=[gallery_image.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "field-image")
        self.assertContains(response, "field-caption")
        self.assertNotContains(response, "field-alt_text")
        self.assertNotContains(response, 'name="alt_text"', html=False)
        self.assertContains(response, 'value="Запис" class="default" name="_save"', html=False)
        self.assertContains(
            response,
            f'href="/admin/pages/galleryimage/{gallery_image.pk}/delete/" class="deletelink">Изтрий</a>',
            html=False,
        )
        self.assertNotContains(response, 'name="_continue"', html=False)
        self.assertNotContains(response, 'name="_addanother"', html=False)

    def test_board_member_change_form_uses_minimal_fields_and_actions(self):
        member = BoardMember.objects.create(
            full_name="Иван Петров",
            slug="ivan-petrov",
            role="Председател",
            short_bio="Кратък текст",
            biography="Подробен текст",
        )
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:pages_boardmember_change", args=[member.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "field-portrait")
        self.assertContains(response, "field-full_name")
        self.assertContains(response, "field-role")
        self.assertContains(response, "field-phone")
        self.assertContains(response, "field-email")
        self.assertContains(response, "field-short_bio")
        self.assertContains(response, '<label for="id_short_bio">Биография:</label>', html=False)
        self.assertNotContains(response, "field-portrait_preview")
        self.assertNotContains(response, "field-slug")
        self.assertNotContains(response, 'name="slug"', html=False)
        self.assertNotContains(response, "Кратка биография:")
        self.assertNotContains(response, "field-biography")
        self.assertNotContains(response, 'name="biography"', html=False)
        self.assertNotContains(response, "fieldset-heading\">Публикация")
        self.assertNotContains(response, "field-is_published")
        self.assertNotContains(response, "field-sort_order")
        self.assertContains(response, 'value="Запис" class="default" name="_save"', html=False)
        self.assertContains(
            response,
            f'href="/admin/pages/boardmember/{member.pk}/delete/" class="deletelink">Изтрий</a>',
            html=False,
        )
        self.assertNotContains(response, 'name="_continue"', html=False)
        self.assertNotContains(response, 'name="_addanother"', html=False)

    def test_board_member_changelist_hides_publication_order_columns_and_filters(self):
        BoardMember.objects.create(
            full_name="Иван Петров",
            slug="ivan-petrov",
            role="Председател",
        )
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:pages_boardmember_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "column-portrait_preview")
        self.assertContains(response, "column-full_name")
        self.assertContains(response, "column-role")
        self.assertContains(response, "column-phone")
        self.assertContains(response, "column-updated_at")
        self.assertNotContains(response, "column-is_published")
        self.assertNotContains(response, "column-sort_order")
        self.assertNotContains(response, "Публикувано")
        self.assertNotContains(response, 'id="changelist-filter"')
        self.assertNotContains(response, "По Публикувано")
        self.assertNotContains(response, "is_published__exact")

    def test_board_member_add_generates_slug_and_publishes_member(self):
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("admin:pages_boardmember_add"),
            {
                "full_name": "Мария Георгиева",
                "role": "Секретар",
                "phone": "0888123456",
                "email": "maria@example.bg",
                "short_bio": "Биография за сайта",
                "_save": "Запис",
            },
        )

        self.assertEqual(response.status_code, 302)
        member = BoardMember.objects.get(full_name="Мария Георгиева")
        self.assertTrue(member.slug)
        self.assertTrue(member.is_published)
