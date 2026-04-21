import base64
from datetime import timedelta
from tempfile import TemporaryDirectory

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from core.models import FooterLink, SiteSettings
from inquiries.models import InquirySubmission, InquiryType
from pages.models import HistoryEntry, HomePage, LibraryImage, Page, PageType
from programs.models import Program, ProgramCategory, ProgramSession
from stories.models import Story, StoryAttachment

from .context_processors import FACEBOOK_PAGE_URL, site_context
from .forms import ContactInquiryForm, CookiePreferencesForm, EnrollmentInquiryForm


PNG_BYTES = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4////fwAJ+wP9KobjigAAAABJRU5ErkJggg=="
)


class SeedSiteContentCommandTests(TestCase):
    def test_seed_command_populates_review_content(self):
        call_command("seed_site_content")

        self.assertTrue(SiteSettings.objects.exists())
        self.assertTrue(
            FooterLink.objects.filter(
                title="Facebook",
                url=FACEBOOK_PAGE_URL,
                open_in_new_tab=True,
            ).exists()
        )
        self.assertTrue(HomePage.objects.exists())
        self.assertEqual(
            list(ProgramCategory.objects.order_by("sort_order").values_list("name", "slug")),
            [("Деца", "kids"), ("Възрастни", "adults")],
        )
        self.assertGreaterEqual(Program.objects.count(), 4)
        self.assertGreaterEqual(Story.objects.count(), 3)
        self.assertTrue(StoryAttachment.objects.exists())
        self.assertTrue(ProgramSession.objects.filter(program__isnull=False).exists())
        self.assertFalse(Page.objects.filter(slug="membership").exists())

    def test_seed_command_is_idempotent(self):
        call_command("seed_site_content")
        baseline_counts = {
            "programs": Program.objects.count(),
            "stories": Story.objects.count(),
            "story_attachments": StoryAttachment.objects.count(),
            "pages": Page.objects.count(),
            "sessions": ProgramSession.objects.count(),
        }

        call_command("seed_site_content")

        self.assertEqual(baseline_counts["programs"], Program.objects.count())
        self.assertEqual(baseline_counts["stories"], Story.objects.count())
        self.assertEqual(baseline_counts["story_attachments"], StoryAttachment.objects.count())
        self.assertEqual(baseline_counts["pages"], Page.objects.count())
        self.assertEqual(baseline_counts["sessions"], ProgramSession.objects.count())


class PublicPagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_site_content")
        cls.program = Program.objects.first()
        cls.category = cls.program.category
        cls.project = Story.objects.first()
        cls.charter_page = Page.objects.get(slug="charter")

    def test_homepage_loads(self):
        response = self.client.get(reverse("cms:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Школи и клубове")
        self.assertContains(response, reverse("cms:programs"))
        self.assertContains(response, reverse("cms:projects"))
        self.assertContains(response, reverse("cms:gallery"))
        self.assertContains(response, reverse("cms:library"))
        self.assertContains(response, "За Нас")
        self.assertContains(response, reverse("cms:page_detail", kwargs={"slug": "charter"}))
        self.assertContains(response, reverse("cms:history"))
        self.assertContains(response, reverse("cms:board"))
        self.assertNotContains(response, "/info/membership/")
        self.assertNotContains(response, 'href="index.html"')
        self.assertNotContains(response, 'href="contact.html"')

    @override_settings(PUBLIC_SITE_URL="https://www.kirilimetodii1926.com")
    def test_homepage_exposes_search_metadata(self):
        response = self.client.get(reverse("cms:home"))
        html = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            '<meta name="description" content="Официален сайт на Народно читалище „Св. св. Кирил и Методий – 1926“',
            html,
        )
        self.assertIn('<link rel="canonical" href="https://www.kirilimetodii1926.com/">', html)
        self.assertIn('<p data-nosnippet>', html)
        self.assertIn('<div class="footer-contact" data-nosnippet>', html)
        self.assertNotIn("Публичен Django сайт", html)

    @override_settings(PUBLIC_SITE_URL="https://www.kirilimetodii1926.com")
    def test_robots_txt_allows_crawling_and_points_to_sitemap(self):
        response = self.client.get(reverse("cms:robots_txt"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain")
        self.assertContains(response, "User-agent: *")
        self.assertContains(response, "Allow: /")
        self.assertContains(response, "Sitemap: https://www.kirilimetodii1926.com/sitemap.xml")

    def test_sitemap_lists_public_urls(self):
        response = self.client.get(reverse("cms:sitemap"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<loc>http://testserver/</loc>")
        self.assertContains(response, f"<loc>http://testserver{reverse('cms:programs')}</loc>")
        self.assertContains(response, f"<loc>http://testserver{self.program.get_absolute_url()}</loc>")
        self.assertContains(response, f"<loc>http://testserver{self.project.get_absolute_url()}</loc>")

    def test_footer_renders_facebook_link(self):
        response = self.client.get(reverse("cms:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "087 782 0388")
        self.assertContains(response, 'href="tel:0877820388"')
        self.assertContains(response, "chitalishtevrajdebna@gmail.com")
        self.assertContains(response, FACEBOOK_PAGE_URL)
        self.assertContains(response, 'class="footer-social-link"')
        self.assertContains(response, 'aria-label="Facebook"')

    def test_homepage_renders_static_hero_photo(self):
        response = self.client.get(reverse("cms:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="hero-photo"')
        self.assertContains(response, "/static/cms/images/homepage-hero.png")

    def test_key_public_routes_load(self):
        routes = [
            (reverse("cms:programs"), "Школи"),
            (reverse("cms:projects"), "Новини"),
            (reverse("cms:gallery"), "Галерия"),
            (reverse("cms:contact"), "Контакти"),
            (reverse("cms:library"), "Библиотека"),
            (reverse("cms:history"), "История"),
            (reverse("cms:board"), "Настоятелство"),
            (reverse("cms:privacy"), "Политика за поверителност"),
            (reverse("cms:cookies"), "Какви бисквитки използваме"),
        ]

        for url, marker in routes:
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Народно читалище „Св. св. Кирил и Методий – 1926“")
                self.assertContains(response, marker)

    def test_membership_page_returns_not_found(self):
        response = self.client.get("/info/membership/")

        self.assertEqual(response.status_code, 404)

    def test_program_detail_loads(self):
        response = self.client.get(self.program.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.program.title)

    def test_program_detail_uses_program_inquiry_phone(self):
        self.program.inquiry_phone = "+359 88 123 4567"
        self.program.save(update_fields=["inquiry_phone"])

        response = self.client.get(self.program.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<p class="program-phone-link">+359 88 123 4567</p>',
            html=True,
        )
        self.assertNotContains(response, '<a class="program-phone-link"')
        self.assertNotContains(response, "program-inquiry-form")
        self.assertNotContains(response, "Изпрати запитване")

    def test_program_detail_falls_back_to_site_phone(self):
        settings_obj = SiteSettings.load()
        settings_obj.phone_primary = "+359 88 999 0000"
        settings_obj.save(update_fields=["phone_primary"])
        self.program.inquiry_phone = ""
        self.program.save(update_fields=["inquiry_phone"])

        response = self.client.get(self.program.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<p class="program-phone-link">+359 88 999 0000</p>',
            html=True,
        )
        self.assertNotContains(response, '<a class="program-phone-link"')

    def test_program_category_page_loads(self):
        response = self.client.get(self.category.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.category.name)
        self.assertContains(response, self.program.get_absolute_url())

    def test_project_detail_loads(self):
        response = self.client.get(self.project.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.title)
        self.assertContains(response, "Повече информация")

    def test_charter_page_renders_as_simple_text_page(self):
        response = self.client.get(self.charter_page.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.charter_page.title)
        self.assertContains(response, "Използвайте страницата за публикуване")
        self.assertNotContains(response, "Публична навигация")
        self.assertNotContains(response, "Внимание")

    def test_cookies_page_renders_simple_policy_content(self):
        response = self.client.get(reverse("cms:cookies"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Какви бисквитки използваме")
        self.assertContains(response, "Необходими бисквитки")
        self.assertNotContains(response, reverse("cms:cookie_preferences"))
        self.assertNotContains(response, 'data-cookie-banner', html=False)

    def test_privacy_page_renders_simple_policy_content(self):
        response = self.client.get(reverse("cms:privacy"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Как обработваме лични данни")
        self.assertContains(response, "Какви данни може да събираме")
        self.assertNotContains(response, 'data-cookie-banner', html=False)

    def test_legacy_about_urls_redirect_to_named_pages(self):
        response = self.client.get("/about/history/")
        self.assertRedirects(response, reverse("cms:history"), fetch_redirect_response=False)

        response = self.client.get("/about/leadership/")
        self.assertRedirects(response, reverse("cms:board"), fetch_redirect_response=False)

    def test_legacy_project_urls_redirect_to_news_routes(self):
        response = self.client.get("/projects/")
        self.assertRedirects(response, reverse("cms:projects"), fetch_redirect_response=False)

        response = self.client.get(f"/projects/{self.project.slug}/")
        self.assertRedirects(response, self.project.get_absolute_url(), fetch_redirect_response=False)

    def test_library_cyrillic_alias_redirects_to_named_page(self):
        response = self.client.get("/библиотека/")

        self.assertRedirects(response, reverse("cms:library"), fetch_redirect_response=False)


class PublishFilteringTests(TestCase):
    def setUp(self):
        today = timezone.localdate()
        self.category = ProgramCategory.objects.create(name="Музика", slug="music")
        self.published_program = Program.objects.create(
            category=self.category,
            title="Публична програма",
            slug="public-program",
            summary="Кратко описание",
            description="Подробно описание",
            is_published=True,
        )
        self.unpublished_program = Program.objects.create(
            category=self.category,
            title="Скрита програма",
            slug="hidden-program",
            summary="Кратко описание",
            description="Подробно описание",
            is_published=False,
        )
        self.published_story = Story.objects.create(
            title="Публична новина",
            slug="public-story",
            excerpt="Кратко резюме",
            body="Подробности",
            published_at=today,
            story_type="news",
        )
        self.unpublished_story = Story.objects.create(
            title="Скрита новина",
            slug="hidden-story",
            excerpt="Кратко резюме",
            body="Подробности",
            published_at=self.published_story.published_at,
            story_type="news",
            is_published=False,
        )
        self.future_story = Story.objects.create(
            title="Бъдеща новина",
            slug="future-story",
            excerpt="Кратко резюме",
            body="Подробности",
            published_at=today + timedelta(days=7),
            story_type="news",
        )
        self.custom_page = Page.objects.create(
            title="Правила",
            slug="rules",
            body="Публични правила",
            is_published=True,
        )
        self.hidden_page = Page.objects.create(
            title="Скрити правила",
            slug="hidden-rules",
            body="Чернова",
            is_published=False,
        )

    def test_program_routes_hide_unpublished_programs(self):
        response = self.client.get(reverse("cms:programs"))

        self.assertContains(response, self.published_program.title)
        self.assertNotContains(response, self.unpublished_program.title)

        detail_response = self.client.get(self.unpublished_program.get_absolute_url())
        self.assertEqual(detail_response.status_code, 404)

    def test_program_list_defaults_to_kids_category(self):
        kids_category = ProgramCategory.objects.create(name="Деца", slug="kids", sort_order=0)
        kids_program = Program.objects.create(
            category=kids_category,
            title="Детска школа",
            slug="kids-school",
            summary="Кратко описание",
            description="Подробно описание",
            is_published=True,
        )

        response = self.client.get(reverse("cms:programs"))

        self.assertContains(response, kids_category.name)
        self.assertContains(response, kids_program.title)
        self.assertNotContains(response, self.published_program.title)
        self.assertNotContains(response, "Пълен публичен индекс")

    def test_program_category_selection_filters_index_in_place(self):
        other_category = ProgramCategory.objects.create(name="Танци", slug="dance")
        other_program = Program.objects.create(
            category=other_category,
            title="Танцова школа",
            slug="dance-school",
            summary="Кратко описание",
            description="Подробно описание",
            is_published=True,
        )

        response = self.client.get(reverse("cms:programs"), {"category": self.category.slug})

        self.assertContains(response, 'id="program-index"')
        self.assertContains(response, f'href="{reverse("cms:programs")}?category={self.category.slug}#program-index"')
        self.assertContains(response, self.category.name)
        self.assertContains(response, self.published_program.title)
        self.assertNotContains(response, other_program.title)

    def test_program_category_all_selection_shows_full_index_without_heading(self):
        other_category = ProgramCategory.objects.create(name="Танци", slug="dance")
        other_program = Program.objects.create(
            category=other_category,
            title="Танцова школа",
            slug="dance-school",
            summary="Кратко описание",
            description="Подробно описание",
            is_published=True,
        )

        response = self.client.get(reverse("cms:programs"), {"category": "all"})

        self.assertContains(response, self.published_program.title)
        self.assertContains(response, other_program.title)
        self.assertNotContains(response, "Пълен публичен индекс")

    def test_story_routes_hide_unpublished_and_future_stories(self):
        response = self.client.get(reverse("cms:projects"))

        self.assertContains(response, self.published_story.title)
        self.assertNotContains(response, self.unpublished_story.title)
        self.assertNotContains(response, self.future_story.title)

        self.assertEqual(self.client.get(self.unpublished_story.get_absolute_url()).status_code, 404)
        self.assertEqual(self.client.get(self.future_story.get_absolute_url()).status_code, 404)

    def test_static_page_route_hides_unpublished_pages(self):
        response = self.client.get(self.custom_page.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.custom_page.title)

        hidden_response = self.client.get(self.hidden_page.get_absolute_url())
        self.assertEqual(hidden_response.status_code, 404)


class FooterNavigationTests(TestCase):
    def test_footer_context_deduplicates_overlapping_links(self):
        Page.objects.create(
            title="Правила",
            slug="rules",
            body="Текст",
            show_in_header=True,
            is_published=True,
        )
        Page.objects.create(
            title="История",
            slug="history",
            body="Текст",
            page_type=PageType.HISTORY,
            show_in_footer=True,
            is_published=True,
        )
        charter_page = Page.objects.create(
            title="Устав",
            slug="charter",
            body="Текст",
            page_type=PageType.CHARTER,
            show_in_footer=True,
            is_published=True,
        )
        privacy_page = Page.objects.create(
            title="Политика за поверителност",
            slug="privacy",
            body="Текст",
            page_type=PageType.PRIVACY,
            show_in_footer=True,
            is_published=True,
        )
        cookies_page = Page.objects.create(
            title="Политика за бисквитки",
            slug="cookies",
            body="Текст",
            page_type=PageType.COOKIES,
            show_in_footer=True,
            is_published=True,
        )
        FooterLink.objects.create(title="Програми", url="/programs/")
        FooterLink.objects.create(title="История", url="/about/history/")
        FooterLink.objects.create(title="Поверителност", url="/privacy/")
        unique_footer_link = FooterLink.objects.create(title="Дарения", url="/donations/")

        context = site_context(RequestFactory().get("/"))

        self.assertCountEqual(
            [page.pk for page in context["footer_pages"]],
            [charter_page.pk, privacy_page.pk, cookies_page.pk],
        )
        self.assertEqual(
            [link.pk for link in context["footer_links"]],
            [unique_footer_link.pk],
        )

    def test_footer_context_adds_facebook_link_when_missing(self):
        context = site_context(RequestFactory().get("/"))

        self.assertEqual(context["facebook_page_url"], FACEBOOK_PAGE_URL)
        self.assertFalse(any(link.url == FACEBOOK_PAGE_URL for link in context["footer_links"]))

    def test_gallery_api_returns_only_published_images(self):
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                from pages.models import GalleryImage

                GalleryImage.objects.create(
                    image=SimpleUploadedFile("gallery-1.png", PNG_BYTES, content_type="image/png"),
                    caption="Публично изображение",
                    is_published=True,
                )
                GalleryImage.objects.create(
                    image=SimpleUploadedFile("gallery-2.png", PNG_BYTES, content_type="image/png"),
                    caption="Скрито изображение",
                    is_published=False,
                )

                response = self.client.get(reverse("cms:api_gallery"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(response.json()["results"][0]["caption"], "Публично изображение")


class HistoryPageTests(TestCase):
    def setUp(self):
        self.history_page = Page.objects.create(
            page_type=PageType.HISTORY,
            title="История",
            navigation_title="История",
            slug="history",
            intro="Кратък увод",
            body=(
                "<h4>Народно читалище</h4>"
                "<p>Това е HTML текст за историята.</p>"
                '<p><a href="https://example.com/document.doc">Заявление за членство</a></p>'
            ),
            is_published=True,
        )

    def test_history_page_renders_html_body(self):
        response = self.client.get(reverse("cms:history"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h4>Народно читалище</h4>", html=False)
        self.assertContains(response, "Заявление за членство")
        self.assertNotContains(response, "&lt;h4&gt;", html=False)
        self.assertNotContains(response, "Ключови етапи")

    def test_history_page_renders_uploaded_images(self):
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                entry = HistoryEntry.objects.create(
                    page=self.history_page,
                    title="Сграда",
                    image=SimpleUploadedFile("history.png", PNG_BYTES, content_type="image/png"),
                    is_published=True,
                )

                response = self.client.get(reverse("cms:history"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, entry.image.url)
        self.assertNotContains(response, "<figcaption>", html=False)


class LibraryPageTests(TestCase):
    def setUp(self):
        self.library_page, _ = Page.objects.update_or_create(
            slug="library",
            defaults={
                "page_type": PageType.STANDARD,
                "title": "Библиотека",
                "navigation_title": "Библиотека",
                "intro": "Кратък увод",
                "body": (
                    "<h4>Библиотечен фонд</h4>"
                    "<p>Това е HTML текст за библиотеката.</p>"
                    '<p><a href="https://example.com/catalog.pdf">Каталог</a></p>'
                ),
                "callout_title": "Работно време",
                "callout_body": "Понеделник - петък: 09:00 - 18:00\nСъбота: 10:00 - 14:00",
                "is_published": True,
                "show_in_header": True,
            },
        )

    def test_library_page_renders_html_body(self):
        response = self.client.get(reverse("cms:library"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h4>Библиотечен фонд</h4>", html=False)
        self.assertContains(response, "Каталог")
        self.assertContains(response, "Описание")
        self.assertContains(response, "Работно време")
        self.assertContains(response, "Понеделник - петък")
        self.assertNotContains(response, "&lt;h4&gt;", html=False)

    def test_library_page_renders_published_photos(self):
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                published_photo = LibraryImage.objects.create(
                    page=self.library_page,
                    image=SimpleUploadedFile("library.png", PNG_BYTES, content_type="image/png"),
                    caption="Читалня",
                )
                LibraryImage.objects.create(
                    page=self.library_page,
                    image=SimpleUploadedFile("hidden-library.png", PNG_BYTES, content_type="image/png"),
                    caption="Скрита снимка",
                    is_published=False,
                )

                response = self.client.get(reverse("cms:library"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "library-photo-grid")
        self.assertContains(response, published_photo.image.url)
        self.assertContains(response, "Читалня")
        self.assertNotContains(response, "Скрита снимка")
        self.assertNotContains(response, "<h2>Снимки от библиотеката</h2>", html=False)

    def test_library_gallery_renders_above_description(self):
        with TemporaryDirectory() as media_root:
            with override_settings(MEDIA_ROOT=media_root):
                LibraryImage.objects.create(
                    page=self.library_page,
                    image=SimpleUploadedFile("library-order.png", PNG_BYTES, content_type="image/png"),
                )

                response = self.client.get(reverse("cms:library"))

        content = response.content.decode()
        self.assertLess(content.index("library-gallery-section"), content.index("<h2>Описание</h2>"))


class FormUnitTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.category = ProgramCategory.objects.create(name="Театър", slug="theatre")
        self.program = Program.objects.create(
            category=self.category,
            title="Сценична работилница",
            slug="stage-lab",
            summary="Кратко описание",
            description="Подробно описание",
        )

    def test_contact_form_does_not_include_location_field(self):
        form = ContactInquiryForm()

        self.assertNotIn("location", form.fields)

    def test_contact_form_requires_consent(self):
        form = ContactInquiryForm(
            data={
                "full_name": "Тест Потребител",
                "email": "user@example.bg",
                "subject": "Въпрос",
                "message": "Съобщение",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("consent", form.errors)

    def test_contact_form_save_sets_general_inquiry_type(self):
        form = ContactInquiryForm(
            data={
                "full_name": "Тест Потребител",
                "email": "user@example.bg",
                "subject": "Въпрос",
                "message": "Съобщение",
                "consent": "on",
            }
        )

        self.assertTrue(form.is_valid())
        submission = form.save()

        self.assertEqual(submission.inquiry_type, InquiryType.GENERAL)

    def test_enrollment_form_requires_consent(self):
        form = EnrollmentInquiryForm(
            data={
                "full_name": "Тест Потребител",
                "email": "user@example.bg",
                "message": "Искам да се запиша.",
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("consent", form.errors)

    def test_enrollment_form_save_sets_program_and_subject(self):
        form = EnrollmentInquiryForm(
            data={
                "full_name": "Тест Потребител",
                "email": "user@example.bg",
                "message": "Искам да се запиша.",
                "consent": "on",
            }
        )

        self.assertTrue(form.is_valid())
        submission = form.save(program=self.program)

        self.assertEqual(submission.inquiry_type, InquiryType.ENROLLMENT)
        self.assertEqual(submission.program, self.program)
        self.assertEqual(submission.subject, f"Записване за {self.program.title}")

    def test_cookie_preferences_form_rejects_external_redirects(self):
        form = CookiePreferencesForm(data={"analytics": "on", "redirect_to": "https://example.com"})
        request = self.factory.post(reverse("cms:cookie_preferences"))
        request.META["HTTP_HOST"] = "testserver"

        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_redirect_to(request), reverse("cms:cookies"))

    def test_cookie_preferences_form_allows_internal_redirects(self):
        form = CookiePreferencesForm(data={"analytics": "on", "redirect_to": reverse("cms:contact")})
        request = self.factory.post(reverse("cms:cookie_preferences"))
        request.META["HTTP_HOST"] = "testserver"

        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_redirect_to(request), reverse("cms:contact"))


class FormIntegrationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed_site_content")
        cls.program = Program.objects.first()

    def test_contact_page_uses_admin_managed_intro_content(self):
        settings_obj = SiteSettings.load()
        settings_obj.contact_page_title = "Свържете се с нас"
        settings_obj.contact_page_intro = "Редактиран увод от администрацията."
        settings_obj.contact_page_hours_label = "Приемно време"
        settings_obj.contact_page_map_label = "Как да ни намерите:"
        settings_obj.contact_page_form_heading = "Пишете ни чрез формата:"
        settings_obj.contact_page_submit_label = "Изпрати съобщение"
        settings_obj.contact_page_privacy_note = "Тестов текст за личните данни."
        settings_obj.location_name = "Основна база"
        settings_obj.address_line = "кв. Враждебна, ул. „8-ма“ 47"
        settings_obj.phone_primary = "087 782 0388"
        settings_obj.phone_secondary = "+359 88 111 2222"
        settings_obj.email = "contact@example.bg"
        settings_obj.working_hours_summary = "Всеки делничен ден, 10:00 - 17:00"
        settings_obj.save(
            update_fields=[
                "contact_page_title",
                "contact_page_intro",
                "contact_page_hours_label",
                "contact_page_map_label",
                "contact_page_form_heading",
                "contact_page_submit_label",
                "contact_page_privacy_note",
                "location_name",
                "address_line",
                "phone_primary",
                "phone_secondary",
                "email",
                "working_hours_summary",
            ]
        )

        response = self.client.get(reverse("cms:contact"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Свържете се с нас")
        self.assertContains(response, "Редактиран увод от администрацията.")
        self.assertContains(response, "кв. Враждебна, ул. „8-ма“ 47")
        self.assertContains(response, "087 782 0388")
        self.assertContains(response, 'href="tel:0877820388"')
        self.assertContains(response, "+359 88 111 2222")
        self.assertContains(response, "contact@example.bg")
        self.assertContains(response, "Всеки делничен ден, 10:00 - 17:00")
        self.assertContains(response, "Приемно време")
        self.assertContains(response, "Как да ни намерите:")
        self.assertContains(response, "Пишете ни чрез формата:")
        self.assertContains(response, "Изпрати съобщение")
        self.assertContains(response, "Тестов текст за личните данни.")

    def test_contact_page_does_not_fallback_to_placeholder_intro(self):
        settings_obj = SiteSettings.load()
        settings_obj.contact_page_intro = ""
        settings_obj.save(update_fields=["contact_page_intro"])

        response = self.client.get(reverse("cms:contact"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Всички публични контакти са събрани")

    def test_contact_form_creates_submission(self):
        response = self.client.post(
            reverse("cms:contact"),
            data={
                "full_name": "Тест Потребител",
                "email": "test@example.bg",
                "phone": "+359 88 555 5555",
                "subject": "Общо запитване",
                "message": "Здравейте, интересувам се от работното време.",
                "consent": "on",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(InquirySubmission.objects.count(), 1)

    def test_contact_form_invalid_post_keeps_user_on_page(self):
        response = self.client.post(
            reverse("cms:contact"),
            data={
                "full_name": "Тест Потребител",
                "email": "test@example.bg",
                "subject": "Общо запитване",
                "message": "Без съгласие",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Необходимо е съгласие")
        self.assertEqual(InquirySubmission.objects.count(), 0)

    def test_cookie_banner_defaults_to_no_saved_choice(self):
        response = self.client.get(reverse("cms:home"))

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["cookie_preferences"].has_choice)
        self.assertFalse(response.context["cookie_preferences"].analytics_enabled)

    def test_cookie_preferences_are_saved_in_cookie(self):
        response = self.client.post(
            reverse("cms:cookie_preferences"),
            data={
                "analytics": "on",
                "redirect_to": reverse("cms:home"),
            },
        )

        self.assertRedirects(response, reverse("cms:home"), fetch_redirect_response=False)
        self.assertIn(settings.COOKIE_CONSENT_COOKIE_NAME, response.cookies)

        follow_response = self.client.get(reverse("cms:home"))

        self.assertEqual(follow_response.status_code, 200)
        self.assertTrue(follow_response.context["cookie_preferences"].has_choice)
        self.assertTrue(follow_response.context["cookie_preferences"].analytics_enabled)
