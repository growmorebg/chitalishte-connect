from dataclasses import dataclass

from django.conf import settings
from django.core import signing


COOKIE_CONSENT_SALT = "cms.cookie-preferences"


@dataclass(frozen=True)
class CookiePreferences:
    has_choice: bool = False
    analytics_enabled: bool = False

    @property
    def necessary_enabled(self):
        return True

    def as_cookie_value(self):
        return signing.dumps(
            {
                "analytics_enabled": self.analytics_enabled,
            },
            salt=COOKIE_CONSENT_SALT,
        )


def get_cookie_preferences(request):
    raw_value = request.COOKIES.get(settings.COOKIE_CONSENT_COOKIE_NAME)
    if not raw_value:
        return CookiePreferences()

    try:
        payload = signing.loads(raw_value, salt=COOKIE_CONSENT_SALT)
    except signing.BadSignature:
        return CookiePreferences()

    return CookiePreferences(
        has_choice=True,
        analytics_enabled=bool(payload.get("analytics_enabled")),
    )


def set_cookie_preferences(response, preferences):
    response.set_cookie(
        settings.COOKIE_CONSENT_COOKIE_NAME,
        preferences.as_cookie_value(),
        max_age=settings.COOKIE_CONSENT_COOKIE_MAX_AGE,
        secure=settings.COOKIE_CONSENT_COOKIE_SECURE,
        httponly=settings.COOKIE_CONSENT_COOKIE_HTTPONLY,
        samesite=settings.COOKIE_CONSENT_COOKIE_SAMESITE,
    )
    return response
