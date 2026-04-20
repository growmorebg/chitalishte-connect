from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import InquirySubmission, InquiryType


class InquiryAdminTests(TestCase):
    def setUp(self):
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            email="admin@example.bg",
            password="password123",
        )
        self.submission = InquirySubmission.objects.create(
            inquiry_type=InquiryType.GENERAL,
            full_name="Тест Потребител",
            email="user@example.bg",
            phone="+359881234567",
            subject="Тестово запитване",
            message="Искам повече информация.",
        )

    def test_admin_can_view_submission_list(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(reverse("admin:inquiries_inquirysubmission_changelist"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.submission.subject)
        self.assertContains(response, self.submission.full_name)

    def test_admin_can_view_submission_detail(self):
        self.client.force_login(self.admin_user)

        response = self.client.get(
            reverse("admin:inquiries_inquirysubmission_change", args=[self.submission.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.submission.subject)
        self.assertContains(response, self.submission.message)


class InquiryNotificationTests(TestCase):
    @override_settings(
        INQUIRY_NOTIFICATION_ENABLED=True,
        INQUIRY_NOTIFICATION_RECIPIENTS=["team@example.bg"],
        INQUIRY_NOTIFICATION_FROM_EMAIL="noreply@example.bg",
    )
    def test_contact_submission_sends_notification_when_enabled(self):
        response = self.client.post(
            reverse("cms:contact"),
            data={
                "full_name": "Мария Тестова",
                "email": "maria@example.bg",
                "phone": "+359 88 777 7777",
                "subject": "Въпрос за програмите",
                "message": "Здравейте, интересувам се от предстоящи занимания.",
                "consent": "on",
            },
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(InquirySubmission.objects.count(), 1)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["team@example.bg"])
        self.assertIn("Въпрос за програмите", mail.outbox[0].subject)
        self.assertIn("Мария Тестова", mail.outbox[0].body)
