from datetime import date, time

from django.contrib import admin
from django.core.exceptions import ValidationError
from django.test import TestCase

from .models import Program, ProgramCategory, ProgramSession


class ProgramModelTests(TestCase):
    def setUp(self):
        self.category = ProgramCategory.objects.create(name="Музика", slug="music")

    def test_program_manager_published_returns_only_published_records(self):
        visible = Program.objects.create(
            category=self.category,
            title="Видима програма",
            slug="visible-program",
            summary="Кратко описание",
            description="Подробно описание",
            is_published=True,
        )
        Program.objects.create(
            category=self.category,
            title="Скрита програма",
            slug="hidden-program",
            summary="Кратко описание",
            description="Подробно описание",
            is_published=False,
        )

        self.assertQuerySetEqual(
            Program.objects.published(),
            [visible],
            transform=lambda item: item,
        )

    def test_program_session_rejects_end_time_before_start_time(self):
        program = Program.objects.create(
            category=self.category,
            title="Програма",
            slug="program",
            summary="Кратко описание",
            description="Подробно описание",
        )
        session = ProgramSession(
            program=program,
            title="Сесия",
            date=date(2026, 4, 1),
            time=time(18, 0),
            end_time=time(17, 30),
        )

        with self.assertRaises(ValidationError):
            session.full_clean()

    def test_program_session_allows_open_end_time(self):
        program = Program.objects.create(
            category=self.category,
            title="Програма",
            slug="program-open",
            summary="Кратко описание",
            description="Подробно описание",
        )
        session = ProgramSession(
            program=program,
            title="Сесия",
            date=date(2026, 4, 1),
            time=time(18, 0),
            end_time=None,
        )

        session.full_clean()


class ProgramAdminTests(TestCase):
    def test_program_category_is_registered_in_admin(self):
        self.assertTrue(admin.site.is_registered(ProgramCategory))

        admin_instance = admin.site._registry[ProgramCategory]

        self.assertEqual(admin_instance.prepopulated_fields, {"slug": ("name",)})
        self.assertIn("is_published", admin_instance.list_filter)

    def test_program_session_is_not_registered_in_admin(self):
        self.assertFalse(admin.site.is_registered(ProgramSession))
