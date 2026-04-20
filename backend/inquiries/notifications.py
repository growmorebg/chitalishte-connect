import logging

from django.conf import settings
from django.core.mail import EmailMultiAlternatives


logger = logging.getLogger(__name__)


def send_submission_notification(submission):
    recipients = getattr(settings, "INQUIRY_NOTIFICATION_RECIPIENTS", [])
    if not settings.INQUIRY_NOTIFICATION_ENABLED or not recipients:
        return False

    subject_prefix = settings.INQUIRY_NOTIFICATION_SUBJECT_PREFIX.strip()
    subject = f"{subject_prefix} {submission.get_inquiry_type_display()}: {submission.subject}".strip()
    lines = [
        "Получено е ново запитване от публичния сайт.",
        "",
        f"Тип: {submission.get_inquiry_type_display()}",
        f"Име: {submission.full_name}",
        f"Имейл: {submission.email}",
        f"Телефон: {submission.phone or '-'}",
        f"Тема: {submission.subject}",
        f"Програма: {submission.program.title if submission.program else '-'}",
        f"Статус: {submission.get_status_display()}",
        "",
        "Съобщение:",
        submission.message,
        "",
        f"Администрация: {submission.get_admin_url()}",
    ]

    message = EmailMultiAlternatives(
        subject=subject,
        body="\n".join(lines),
        from_email=settings.INQUIRY_NOTIFICATION_FROM_EMAIL,
        to=recipients,
        reply_to=[submission.email],
    )
    try:
        message.send()
    except Exception:
        logger.exception("Failed to send inquiry notification for submission %s", submission.pk)
        return False
    return True
