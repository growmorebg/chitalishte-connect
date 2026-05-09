from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import TestCase
from django.utils import timezone

from .models import Story, StoryAttachment, StoryType


class StoryModelTests(TestCase):
    def test_story_manager_published_returns_only_published_records(self):
        visible = Story.objects.create(
            title="Видима история",
            slug="visible-story",
            excerpt="Кратко резюме",
            body="Подробности",
            published_at=timezone.localdate(),
            story_type=StoryType.STORY,
            is_published=True,
        )
        Story.objects.create(
            title="Скрита история",
            slug="hidden-story",
            excerpt="Кратко резюме",
            body="Подробности",
            published_at=timezone.localdate(),
            story_type=StoryType.STORY,
            is_published=False,
        )

        self.assertQuerySetEqual(
            Story.objects.published(),
            [visible],
            transform=lambda item: item,
        )

    def test_story_attachment_requires_file_or_external_url(self):
        story = Story.objects.create(
            title="История",
            slug="story",
            excerpt="Кратко резюме",
            body="Подробности",
            published_at=timezone.localdate(),
        )
        attachment = StoryAttachment(story=story, title="Ресурс")

        with self.assertRaises(ValidationError):
            attachment.full_clean()

    def test_story_attachment_allows_external_url(self):
        story = Story.objects.create(
            title="История",
            slug="story-with-url",
            excerpt="Кратко резюме",
            body="Подробности",
            published_at=timezone.localdate(),
        )
        attachment = StoryAttachment(
            story=story,
            title="Ресурс",
            external_url="https://example.bg/resource",
        )

        attachment.full_clean()

    def test_story_attachment_detects_image_files(self):
        story = Story.objects.create(
            title="История",
            slug="story-with-image",
            excerpt="Кратко резюме",
            body="Подробности",
            published_at=timezone.localdate(),
        )
        image_attachment = StoryAttachment(
            story=story,
            title="Снимка",
            file="project_attachments/photo.JPG",
        )
        document_attachment = StoryAttachment(
            story=story,
            title="Документ",
            file="project_attachments/program.pdf",
        )

        self.assertTrue(image_attachment.is_image)
        self.assertFalse(document_attachment.is_image)


class StoryAdminPreviewTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.bg",
            password="password123",
        )
        self.story = Story.objects.create(
            title="Чернова новина",
            slug="draft-news",
            excerpt="Кратко резюме",
            body="Текст преди публикуване.",
            published_at=timezone.localdate() + timedelta(days=7),
            story_type=StoryType.NEWS,
            is_published=False,
        )

    def test_admin_preview_renders_unpublished_story(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:stories_story_preview", args=[self.story.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Robots-Tag"], "noindex, nofollow")
        self.assertContains(response, self.story.title)
        self.assertContains(response, self.story.body)

    def test_admin_change_form_matches_add_form_with_delete_action(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:stories_story_change", args=[self.story.pk]))

        self.assertContains(response, 'value="Запази" name="_save"', html=False)
        self.assertNotContains(response, "Запази и прегледай")
        self.assertContains(response, reverse("admin:stories_story_delete", args=[self.story.pk]))
        self.assertNotContains(response, reverse("admin:stories_story_preview", args=[self.story.pk]))
        self.assertNotContains(response, "cc-row-action--preview")
        self.assertNotContains(response, "Кратък адрес")
        self.assertNotContains(response, "Кратко резюме")
        self.assertNotContains(response, "Публикувано")
        self.assertNotContains(response, 'name="_continue"')
        self.assertNotContains(response, 'name="_addanother"')

    def test_admin_changelist_shows_compact_preview_and_publish_actions(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:stories_story_changelist"))

        self.assertContains(response, "cc-row-action--preview")
        self.assertContains(response, reverse("admin:stories_story_preview", args=[self.story.pk]))
        self.assertContains(response, "cc-row-action--publish")
        self.assertContains(response, f'name="_toggle_publish" value="{self.story.pk}"')
        self.assertContains(response, "Публикувай")
        self.assertNotContains(response, "column-is_featured")
        self.assertNotContains(response, "is_featured__exact")
        self.assertNotContains(response, "По Показвай на началната страница")
        self.assertNotContains(response, '<div class="actions">', html=False)
        self.assertNotContains(response, "action-checkbox")
        self.assertNotContains(response, 'name="_selected_action"', html=False)

    def test_admin_changelist_publish_button_publishes_and_unpublishes_story(self):
        self.client.force_login(self.admin_user)
        changelist_url = reverse("admin:stories_story_changelist")

        publish_response = self.client.post(changelist_url, {"_toggle_publish": str(self.story.pk)})
        self.story.refresh_from_db()

        self.assertRedirects(
            publish_response,
            changelist_url,
            fetch_redirect_response=False,
        )
        self.assertTrue(self.story.is_published)

        unpublish_response = self.client.post(changelist_url, {"_toggle_publish": str(self.story.pk)})
        self.story.refresh_from_db()

        self.assertRedirects(
            unpublish_response,
            changelist_url,
            fetch_redirect_response=False,
        )
        self.assertFalse(self.story.is_published)

    def test_admin_publish_toggle_url_publishes_and_unpublishes_story(self):
        self.client.force_login(self.admin_user)
        toggle_url = reverse("admin:stories_story_toggle_publish", args=[self.story.pk])

        publish_response = self.client.post(toggle_url, {"next": reverse("admin:stories_story_changelist")})
        self.story.refresh_from_db()

        self.assertRedirects(
            publish_response,
            reverse("admin:stories_story_changelist"),
            fetch_redirect_response=False,
        )
        self.assertTrue(self.story.is_published)

        unpublish_response = self.client.post(toggle_url, {"next": reverse("admin:stories_story_changelist")})
        self.story.refresh_from_db()

        self.assertRedirects(
            unpublish_response,
            reverse("admin:stories_story_changelist"),
            fetch_redirect_response=False,
        )
        self.assertFalse(self.story.is_published)

    def test_admin_add_form_hides_draft_only_fields_and_buttons(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:stories_story_add"))

        self.assertContains(response, 'value="Запази" name="_save"', html=False)
        self.assertNotContains(response, "Запази и прегледай")
        self.assertNotContains(response, "Преглед:")
        self.assertNotContains(response, "Кратък адрес")
        self.assertNotContains(response, "Кратко резюме")
        self.assertNotContains(response, "Публикувано")
        self.assertNotContains(response, "field-sort_order")
        self.assertNotContains(response, 'name="sort_order"', html=False)
        self.assertNotContains(response, 'name="_continue"')
        self.assertNotContains(response, 'name="_addanother"')
        self.assertContains(response, "Снимки към публикации")
        self.assertContains(response, "attachments-__prefix__-file")
        self.assertNotContains(response, "attachments-__prefix__-sort_order")
        self.assertNotContains(response, "column-sort_order")
        self.assertNotContains(response, "column-image_preview")
        self.assertNotContains(response, "attachments-__prefix__-title")
        self.assertNotContains(response, "attachments-__prefix__-external_url")
        self.assertNotContains(response, "attachments-__prefix__-description")

    def test_admin_add_save_redirects_to_changelist(self):
        self.client.force_login(self.admin_user)
        changelist_url = reverse("admin:stories_story_changelist")

        response = self.client.post(
            reverse("admin:stories_story_add"),
            {
                "story_type": StoryType.NEWS,
                "title": "Нова чернова",
                "body": "Текст преди публикуване.",
                "published_at": timezone.localdate().isoformat(),
                "sort_order": "0",
                "_save": "Запази",
                "attachments-TOTAL_FORMS": "0",
                "attachments-INITIAL_FORMS": "0",
                "attachments-MIN_NUM_FORMS": "0",
                "attachments-MAX_NUM_FORMS": "1000",
            },
        )
        story = Story.objects.get(title="Нова чернова")

        self.assertRedirects(
            response,
            changelist_url,
            fetch_redirect_response=False,
        )
        self.assertEqual(story.slug, "publication")
        self.assertEqual(story.excerpt, "Текст преди публикуване.")
        self.assertFalse(story.is_published)

    def test_admin_change_save_redirects_to_changelist(self):
        self.client.force_login(self.admin_user)
        changelist_url = reverse("admin:stories_story_changelist")

        response = self.client.post(
            reverse("admin:stories_story_change", args=[self.story.pk]),
            {
                "story_type": StoryType.NEWS,
                "title": "Обновена чернова",
                "body": "Обновен текст.",
                "published_at": self.story.published_at.isoformat(),
                "is_featured": "on",
                "sort_order": "0",
                "_save": "Запази",
                "attachments-TOTAL_FORMS": "0",
                "attachments-INITIAL_FORMS": "0",
                "attachments-MIN_NUM_FORMS": "0",
                "attachments-MAX_NUM_FORMS": "1000",
            },
        )

        self.assertRedirects(
            response,
            changelist_url,
            fetch_redirect_response=False,
        )
        self.story.refresh_from_db()
        self.assertEqual(self.story.title, "Обновена чернова")

    def test_admin_add_save_auto_titles_uploaded_attachment(self):
        self.client.force_login(self.admin_user)
        changelist_url = reverse("admin:stories_story_changelist")

        response = self.client.post(
            reverse("admin:stories_story_add"),
            {
                "story_type": StoryType.NEWS,
                "title": "Чернова с файл",
                "body": "Текст преди публикуване.",
                "published_at": timezone.localdate().isoformat(),
                "sort_order": "0",
                "_save": "Запази",
                "attachments-TOTAL_FORMS": "1",
                "attachments-INITIAL_FORMS": "0",
                "attachments-MIN_NUM_FORMS": "0",
                "attachments-MAX_NUM_FORMS": "1000",
                "attachments-0-sort_order": "0",
                "attachments-0-file": SimpleUploadedFile(
                    "program.pdf",
                    b"test file",
                    content_type="application/pdf",
                ),
            },
        )
        story = Story.objects.get(title="Чернова с файл")
        attachment = story.attachments.get()

        self.assertRedirects(
            response,
            changelist_url,
            fetch_redirect_response=False,
        )
        self.assertEqual(attachment.title, "program.pdf")
        self.assertTrue(attachment.file)

    def test_admin_change_form_displays_attachment_file_preview_in_file_field(self):
        StoryAttachment.objects.create(
            story=self.story,
            title="Снимка",
            file="project_attachments/photo.jpg",
        )
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:stories_story_change", args=[self.story.pk]))

        self.assertContains(response, "cms/js/admin_story_attachments.js")
        self.assertContains(response, 'name="attachments-0-DELETE"', html=False)
        self.assertNotContains(response, "field-sort_order")
        self.assertNotContains(response, 'name="sort_order"', html=False)
        self.assertNotContains(response, "column-sort_order")
        self.assertNotContains(response, "column-image_preview")
        self.assertNotContains(response, 'name="attachments-0-sort_order"', html=False)
        self.assertContains(response, "story-attachment-preview")
        self.assertContains(response, 'src="/media/project_attachments/photo.jpg"', html=False)
        self.assertContains(response, 'name="attachments-0-file"', html=False)
        self.assertNotContains(response, "clearable-file-input")
        self.assertNotContains(response, "Изчисти")

    def test_admin_change_form_loads_cover_image_clear_button_helper(self):
        self.story.cover_image = "projects/cover.jpg"
        self.story.save(update_fields=["cover_image"])
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:stories_story_change", args=[self.story.pk]))

        self.assertContains(response, 'id="cover_image-clear_id"', html=False)
        self.assertContains(response, "cc-admin-current-file__preview")
        self.assertContains(response, 'src="/media/projects/cover.jpg"', html=False)
        self.assertContains(response, 'name="cover_image"', html=False)
        self.assertNotContains(response, '<p class="file-upload">Сега:', html=False)
        self.assertNotContains(response, ">projects/cover.jpg</a>", html=False)
        self.assertContains(response, "cms/js/admin_story_attachments.js")

    def test_admin_preview_requires_staff_login(self):
        response = self.client.get(reverse("admin:stories_story_preview", args=[self.story.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin:login"), response["Location"])

    def test_public_route_still_hides_unpublished_story(self):
        response = self.client.get(self.story.get_absolute_url())

        self.assertEqual(response.status_code, 404)
