from datetime import date, time

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from .models import Instructor, PricingBlock, Program, ProgramCategory, ProgramSession


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
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password",
        )

    def test_program_category_is_registered_in_admin(self):
        self.assertTrue(admin.site.is_registered(ProgramCategory))

        admin_instance = admin.site._registry[ProgramCategory]

        self.assertEqual(admin_instance.prepopulated_fields, {"slug": ("name",)})
        self.assertEqual(admin_instance.list_display, ("name",))
        self.assertEqual(admin_instance.list_filter, ())
        self.assertIsNone(admin_instance.actions)

    def test_program_category_changelist_only_shows_name_column_without_filters(self):
        ProgramCategory.objects.create(name="Деца", slug="kids")
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:programs_programcategory_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "column-name")
        self.assertContains(response, ">Име<", html=False)
        self.assertNotContains(response, "action-checkbox")
        self.assertNotContains(response, "column-slug")
        self.assertNotContains(response, "column-is_published")
        self.assertNotContains(response, "column-sort_order")
        self.assertNotContains(response, 'id="changelist-filter"', html=False)
        self.assertNotContains(response, "is_published__exact")

    def test_program_category_add_form_hides_slug_and_extra_buttons(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:programs_programcategory_add"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "field-name")
        self.assertContains(response, "field-description")
        self.assertNotContains(response, "Кратък адрес")
        self.assertNotContains(response, 'name="slug"', html=False)
        self.assertNotContains(response, "fieldset-heading\">Публикация")
        self.assertNotContains(response, "field-is_published")
        self.assertNotContains(response, "field-sort_order")
        self.assertContains(response, 'value="Запис" class="default" name="_save"', html=False)
        self.assertNotContains(response, 'name="_continue"', html=False)
        self.assertNotContains(response, 'name="_addanother"', html=False)

    def test_program_category_change_form_hides_slug_publication_and_limits_actions(self):
        category = ProgramCategory.objects.create(name="Деца", slug="kids", sort_order=1)
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:programs_programcategory_change", args=[category.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "field-name")
        self.assertContains(response, "field-description")
        self.assertNotContains(response, "field-slug")
        self.assertNotContains(response, 'name="slug"', html=False)
        self.assertNotContains(response, "fieldset-heading\">Публикация")
        self.assertNotContains(response, "field-is_published")
        self.assertNotContains(response, "field-sort_order")
        self.assertContains(response, 'value="Запис" class="default" name="_save"', html=False)
        self.assertContains(
            response,
            f'href="/admin/programs/programcategory/{category.pk}/delete/" class="deletelink">Изтрий</a>',
            html=False,
        )
        self.assertNotContains(response, 'name="_continue"', html=False)
        self.assertNotContains(response, 'name="_addanother"', html=False)

    def test_program_category_add_save_generates_unique_slug(self):
        ProgramCategory.objects.create(name="Съществуваща категория", slug="program-category")
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("admin:programs_programcategory_add"),
            {
                "name": "Нова категория",
                "description": "Описание",
                "is_published": "on",
                "sort_order": "0",
                "_save": "Запис",
            },
        )
        category = ProgramCategory.objects.get(name="Нова категория")

        self.assertRedirects(
            response,
            reverse("admin:programs_programcategory_changelist"),
            fetch_redirect_response=False,
        )
        self.assertEqual(category.slug, "program-category-2")
        self.assertTrue(category.is_published)
        self.assertEqual(category.sort_order, 0)

    def test_program_session_is_not_registered_in_admin(self):
        self.assertFalse(admin.site.is_registered(ProgramSession))

    def test_instructor_add_form_hides_generated_fields_and_limits_actions(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:programs_instructor_add"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "field-portrait")
        self.assertContains(response, "field-full_name")
        self.assertContains(response, "field-role_title")
        self.assertContains(response, "field-biography")
        self.assertNotContains(response, "field-credentials")
        self.assertNotContains(response, 'name="credentials"', html=False)
        self.assertNotContains(response, "field-portrait_preview")
        self.assertNotContains(response, "field-slug")
        self.assertNotContains(response, 'name="slug"', html=False)
        self.assertNotContains(response, "field-is_published")
        self.assertNotContains(response, 'name="is_published"', html=False)
        self.assertNotContains(response, "field-sort_order")
        self.assertNotContains(response, 'name="sort_order"', html=False)
        self.assertContains(response, 'value="Запис" class="default" name="_save"', html=False)
        self.assertNotContains(response, 'name="_continue"', html=False)
        self.assertNotContains(response, 'name="_addanother"', html=False)

    def test_instructor_changelist_hides_bulk_actions(self):
        Instructor.objects.create(full_name="Meli kozata", role_title="Преподавател", biography="Биография", slug="meli-kozata")
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:programs_instructor_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Meli kozata")
        self.assertNotContains(response, '<div class="actions">', html=False)
        self.assertNotContains(response, "action-checkbox")
        self.assertNotContains(response, 'name="_selected_action"', html=False)

    def test_instructor_changelist_hides_publication_order_columns_and_filters(self):
        Instructor.objects.create(
            full_name="Мели Козата",
            role_title="Преподавател",
            biography="Биография",
            slug="meli-kozata",
        )
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:programs_instructor_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "column-portrait_preview")
        self.assertContains(response, "column-full_name")
        self.assertContains(response, "column-role_title")
        self.assertContains(response, "column-updated_at")
        self.assertNotContains(response, "column-is_published")
        self.assertNotContains(response, "column-sort_order")
        self.assertNotContains(response, "Публикувано")
        self.assertNotContains(response, "Ред")
        self.assertNotContains(response, 'id="changelist-filter"', html=False)
        self.assertNotContains(response, "is_published__exact")

    def test_instructor_add_save_generates_slug_and_uses_defaults(self):
        Instructor.objects.create(full_name="Maria Ivanova", role_title="Преподавател", biography="Биография", slug="maria-ivanova")
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("admin:programs_instructor_add"),
            {
                "full_name": "Maria Ivanova",
                "role_title": "Преподавател",
                "biography": "Подробна биография",
                "email": "",
                "phone": "",
                "_save": "Запис",
            },
        )
        instructor = Instructor.objects.get(biography="Подробна биография")

        self.assertRedirects(
            response,
            reverse("admin:programs_instructor_changelist"),
            fetch_redirect_response=False,
        )
        self.assertEqual(instructor.slug, "maria-ivanova-2")
        self.assertTrue(instructor.is_published)
        self.assertEqual(instructor.sort_order, 0)

    def test_instructor_change_form_hides_generated_fields_and_limits_actions(self):
        instructor = Instructor.objects.create(
            full_name="Мели Козата",
            role_title="Преподавател",
            biography="Биография",
            slug="meli-kozata",
            portrait="instructors/portrait.png",
        )
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:programs_instructor_change", args=[instructor.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "field-portrait")
        self.assertContains(response, "field-full_name")
        self.assertContains(response, "field-role_title")
        self.assertContains(response, "field-biography")
        self.assertNotContains(response, "field-credentials")
        self.assertNotContains(response, 'name="credentials"', html=False)
        self.assertNotContains(response, "field-portrait_preview")
        self.assertNotContains(response, "field-slug")
        self.assertNotContains(response, 'name="slug"', html=False)
        self.assertNotContains(response, "field-is_published")
        self.assertNotContains(response, 'name="is_published"', html=False)
        self.assertNotContains(response, "field-sort_order")
        self.assertNotContains(response, 'name="sort_order"', html=False)
        self.assertContains(response, 'value="Запис" class="default" name="_save"', html=False)
        self.assertContains(
            response,
            f'href="/admin/programs/instructor/{instructor.pk}/delete/" class="deletelink">Изтрий</a>',
            html=False,
        )
        self.assertNotContains(response, 'name="_continue"', html=False)
        self.assertNotContains(response, 'name="_addanother"', html=False)

    def test_program_add_form_hides_generated_publication_fields_and_limits_actions(self):
        ProgramCategory.objects.create(name="Музика", slug="music")
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:programs_program_add"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "field-cover_image")
        self.assertContains(response, "field-category")
        self.assertContains(response, "field-title")
        self.assertContains(response, "field-description")
        self.assertNotContains(response, "field-cover_preview")
        self.assertNotContains(response, "field-slug")
        self.assertNotContains(response, 'name="slug"', html=False)
        self.assertNotContains(response, "field-summary")
        self.assertNotContains(response, 'name="summary"', html=False)
        self.assertNotContains(response, "fieldset-heading\">Публикация")
        self.assertNotContains(response, 'name="is_featured"', html=False)
        self.assertNotContains(response, "field-is_published")
        self.assertNotContains(response, 'name="is_published"', html=False)
        self.assertNotContains(response, 'name="sort_order"', html=False)
        self.assertContains(response, 'value="Запис" class="default" name="_save"', html=False)
        self.assertNotContains(response, 'name="_continue"', html=False)
        self.assertNotContains(response, 'name="_addanother"', html=False)

    def test_program_changelist_hides_publication_order_columns_and_filters(self):
        category = ProgramCategory.objects.create(name="Музика", slug="music")
        Program.objects.create(
            category=category,
            title="Пиано",
            slug="piano",
            summary="Кратко описание",
            description="Подробно описание",
        )
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:programs_program_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "column-cover_preview")
        self.assertContains(response, "column-title")
        self.assertContains(response, "column-category")
        self.assertContains(response, "column-inquiry_phone")
        self.assertContains(response, "column-updated_at")
        self.assertNotContains(response, "column-is_featured")
        self.assertNotContains(response, "column-is_published")
        self.assertNotContains(response, "column-sort_order")
        self.assertNotContains(response, "Показвай на началната страница")
        self.assertNotContains(response, "Публикувано")
        self.assertNotContains(response, "Ред")
        self.assertNotContains(response, "is_featured__exact")
        self.assertNotContains(response, "is_published__exact")

    def test_program_schedule_inline_shows_only_public_schedule_fields(self):
        ProgramCategory.objects.create(name="Музика", slug="music")
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:programs_program_add"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "column-day_label")
        self.assertContains(response, "column-start_time")
        self.assertContains(response, "column-end_time")
        self.assertContains(response, "column-room")
        self.assertContains(response, 'class="column-room">Зала', html=False)
        self.assertNotContains(response, 'name="schedule_entries-__prefix__-sort_order"', html=False)
        self.assertNotContains(response, 'name="schedule_entries-__prefix__-title"', html=False)
        self.assertNotContains(response, 'name="schedule_entries-__prefix__-notes"', html=False)
        self.assertNotContains(response, "Зала или локация")

    def test_program_pricing_inline_hides_sort_order_and_featured_fields(self):
        ProgramCategory.objects.create(name="Музика", slug="music")
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:programs_program_add"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "column-title")
        self.assertContains(response, "column-price_label")
        self.assertContains(response, "column-billing_period")
        self.assertContains(response, "column-description")
        self.assertNotContains(response, 'name="pricing_options-__prefix__-sort_order"', html=False)
        self.assertNotContains(response, 'name="pricing_options-__prefix__-is_featured"', html=False)
        self.assertNotContains(response, "column-is_featured")

    def test_program_gallery_inline_hides_thumbnail_and_sort_order_fields(self):
        ProgramCategory.objects.create(name="Музика", slug="music")
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:programs_program_add"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "column-image")
        self.assertContains(response, "column-caption")
        self.assertNotContains(response, "column-thumbnail")
        self.assertNotContains(response, 'name="gallery_items-__prefix__-sort_order"', html=False)

    def test_program_add_save_generates_slug_summary_and_uses_publication_defaults(self):
        category = ProgramCategory.objects.create(name="Музика", slug="music")
        Program.objects.create(
            category=category,
            title="Existing program",
            slug="program",
            summary="Кратко описание",
            description="Подробно описание",
        )
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("admin:programs_program_add"),
            {
                "category": category.pk,
                "title": "Нова школа",
                "description": "  Подробно   описание за школата.  ",
                "audience": "",
                "age_group": "",
                "level": "",
                "duration": "",
                "location_name": "",
                "inquiry_phone": "",
                "instructors": [],
                "schedule_entries-TOTAL_FORMS": "0",
                "schedule_entries-INITIAL_FORMS": "0",
                "schedule_entries-MIN_NUM_FORMS": "0",
                "schedule_entries-MAX_NUM_FORMS": "1000",
                "pricing_options-TOTAL_FORMS": "0",
                "pricing_options-INITIAL_FORMS": "0",
                "pricing_options-MIN_NUM_FORMS": "0",
                "pricing_options-MAX_NUM_FORMS": "1000",
                "gallery_items-TOTAL_FORMS": "0",
                "gallery_items-INITIAL_FORMS": "0",
                "gallery_items-MIN_NUM_FORMS": "0",
                "gallery_items-MAX_NUM_FORMS": "1000",
                "_save": "Запис",
            },
        )
        program = Program.objects.get(title="Нова школа")

        self.assertRedirects(
            response,
            reverse("admin:programs_program_changelist"),
            fetch_redirect_response=False,
        )
        self.assertEqual(program.slug, "program-2")
        self.assertEqual(program.summary, "Подробно описание за школата.")
        self.assertTrue(program.is_featured)
        self.assertTrue(program.is_published)
        self.assertEqual(program.sort_order, 0)

    def test_program_add_save_marks_pricing_rows_as_featured(self):
        category = ProgramCategory.objects.create(name="Музика", slug="music")
        self.client.force_login(self.admin_user)

        response = self.client.post(
            reverse("admin:programs_program_add"),
            {
                "category": category.pk,
                "title": "Нова школа",
                "description": "Подробно описание",
                "audience": "",
                "age_group": "",
                "level": "",
                "duration": "",
                "location_name": "",
                "inquiry_phone": "",
                "instructors": [],
                "schedule_entries-TOTAL_FORMS": "0",
                "schedule_entries-INITIAL_FORMS": "0",
                "schedule_entries-MIN_NUM_FORMS": "0",
                "schedule_entries-MAX_NUM_FORMS": "1000",
                "pricing_options-TOTAL_FORMS": "1",
                "pricing_options-INITIAL_FORMS": "0",
                "pricing_options-MIN_NUM_FORMS": "0",
                "pricing_options-MAX_NUM_FORMS": "1000",
                "pricing_options-0-title": "Месечен план",
                "pricing_options-0-price_label": "50 лв.",
                "pricing_options-0-billing_period": "месечно",
                "pricing_options-0-description": "Описание",
                "gallery_items-TOTAL_FORMS": "0",
                "gallery_items-INITIAL_FORMS": "0",
                "gallery_items-MIN_NUM_FORMS": "0",
                "gallery_items-MAX_NUM_FORMS": "1000",
                "_save": "Запис",
            },
        )
        program = Program.objects.get(title="Нова школа")
        pricing = PricingBlock.objects.get(program=program)

        self.assertRedirects(
            response,
            reverse("admin:programs_program_changelist"),
            fetch_redirect_response=False,
        )
        self.assertTrue(pricing.is_featured)
        self.assertEqual(pricing.sort_order, 0)

    def test_program_change_form_loads_cover_image_clear_button_helper(self):
        category = ProgramCategory.objects.create(name="Музика", slug="music")
        program = Program.objects.create(
            category=category,
            title="Пиано",
            slug="piano",
            summary="Кратко описание",
            description="Подробно описание",
            cover_image="programs/cover.jpg",
        )
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:programs_program_change", args=[program.pk]))

        self.assertContains(response, "field-cover_image")
        self.assertContains(response, 'id="cover_image-clear_id"', html=False)
        self.assertContains(response, "field-category")
        self.assertContains(response, "field-title")
        self.assertContains(response, "field-description")
        self.assertNotContains(response, "field-cover_preview")
        self.assertNotContains(response, "field-slug")
        self.assertNotContains(response, 'name="slug"', html=False)
        self.assertNotContains(response, "field-summary")
        self.assertNotContains(response, 'name="summary"', html=False)
        self.assertNotContains(response, "fieldset-heading\">Публикация")
        self.assertNotContains(response, 'name="is_featured"', html=False)
        self.assertNotContains(response, "field-is_published")
        self.assertNotContains(response, 'name="is_published"', html=False)
        self.assertNotContains(response, 'name="sort_order"', html=False)
        self.assertContains(response, "cms/js/admin_story_attachments.js")
