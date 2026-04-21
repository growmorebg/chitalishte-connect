from core.models import FooterLink, SiteSettings

from .cookies import get_cookie_preferences
from .forms import CookiePreferencesForm
from .services import (
    get_deduped_footer_navigation,
    get_footer_pages,
    get_header_pages,
    get_public_section_links,
)
from .seo import build_public_url

FACEBOOK_PAGE_URL = "https://www.facebook.com/profile.php?id=61550898774893"


def site_context(request):
    cookie_preferences = get_cookie_preferences(request)
    header_pages = list(get_header_pages())
    footer_link_items = [link for link in FooterLink.objects.published() if link.url != FACEBOOK_PAGE_URL]
    footer_links, footer_pages = get_deduped_footer_navigation(
        footer_links=footer_link_items,
        footer_pages=get_footer_pages(),
        header_pages=header_pages,
    )

    return {
        "site_settings": SiteSettings.load(),
        "footer_links": footer_links,
        "header_pages": header_pages,
        "footer_pages": footer_pages,
        "facebook_page_url": FACEBOOK_PAGE_URL,
        "public_section_links": get_public_section_links(),
        "canonical_url": build_public_url(request),
        "cookie_preferences": cookie_preferences,
        "cookie_form": CookiePreferencesForm(
            initial={
                "analytics": cookie_preferences.analytics_enabled,
                "redirect_to": request.get_full_path(),
            }
        ),
    }
