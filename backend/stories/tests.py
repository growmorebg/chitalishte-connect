from django.core.exceptions import ValidationError
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
