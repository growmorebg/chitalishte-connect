from urllib.parse import urlsplit, urlunsplit

from django.db.models import Count, Q
from django.http import Http404
from django.urls import reverse
from django.utils import timezone

from core.models import SiteSettings
from pages.models import Page
from programs.models import Program, ProgramCategory
from stories.models import Story

from .content import DISABLED_PAGE_SLUGS, HEADER_PAGE_EXCLUDED_SLUGS, PAGE_FALLBACKS, PUBLIC_SECTION_LINKS

FOOTER_PRIMARY_URL_NAMES = (
    "cms:home",
    "cms:programs",
    "cms:projects",
    "cms:gallery",
    "cms:history",
    "cms:board",
    "cms:contact",
)

LEGACY_PUBLIC_PATH_ALIASES = {
    "/about/history": "/history",
    "/about/leadership": "/board",
    "/projects": "/novini",
}


def get_public_section_links():
    return [
        {
            "label": item["label"],
            "url": reverse(item["url_name"]),
        }
        for item in PUBLIC_SECTION_LINKS
    ]


def get_header_pages():
    return (
        Page.objects.published()
        .filter(show_in_header=True)
        .exclude(slug__in=HEADER_PAGE_EXCLUDED_SLUGS + DISABLED_PAGE_SLUGS)
    )


def get_footer_pages():
    return Page.objects.published().filter(show_in_footer=True).exclude(slug__in=DISABLED_PAGE_SLUGS)


def normalize_public_url(url):
    parts = urlsplit(url)
    path = parts.path.rstrip("/") or "/"
    path = LEGACY_PUBLIC_PATH_ALIASES.get(path, path)

    if parts.scheme or parts.netloc:
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, parts.query, ""))

    if parts.query:
        return f"{path}?{parts.query}"

    return path


def get_deduped_footer_navigation(*, footer_links, footer_pages, header_pages):
    seen_urls = {
        normalize_public_url(reverse(url_name))
        for url_name in FOOTER_PRIMARY_URL_NAMES
    }
    seen_urls.update(normalize_public_url(page.get_absolute_url()) for page in header_pages)

    unique_footer_pages = []
    for page in footer_pages:
        normalized_url = normalize_public_url(page.get_absolute_url())
        if normalized_url in seen_urls:
            continue

        unique_footer_pages.append(page)
        seen_urls.add(normalized_url)

    unique_footer_links = []
    for link in footer_links:
        normalized_url = normalize_public_url(link.url)
        if normalized_url in seen_urls:
            continue

        unique_footer_links.append(link)
        seen_urls.add(normalized_url)

    return unique_footer_links, unique_footer_pages


def get_static_page(slug):
    if slug == "leadership":
        slug = "board"
    if slug in DISABLED_PAGE_SLUGS:
        raise Http404("Страницата не е намерена.")

    page = Page.objects.published().filter(slug=slug).first()
    if page:
        return page

    fallback = PAGE_FALLBACKS.get(slug)
    if not fallback:
        raise Http404("Страницата не е намерена.")

    return Page(slug=slug, **fallback)


def get_program_categories():
    return (
        ProgramCategory.objects.published()
        .annotate(
            program_count=Count(
                "programs",
                filter=Q(programs__is_published=True),
                distinct=True,
            )
        )
        .order_by("sort_order", "name")
    )


def get_program_queryset():
    return (
        Program.objects.published()
        .select_related("category")
        .prefetch_related("instructors", "pricing_options")
        .order_by("sort_order", "title")
    )


def get_story_queryset():
    return (
        Story.objects.published()
        .filter(published_at__lte=timezone.localdate())
        .order_by("-published_at", "sort_order", "-id")
    )


def get_featured_items(queryset, *, limit):
    featured = list(queryset.filter(is_featured=True)[:limit])
    return featured or list(queryset[:limit])


def get_featured_programs(limit=6):
    return get_featured_items(get_program_queryset(), limit=limit)


def get_featured_stories(limit=4):
    return get_featured_items(get_story_queryset(), limit=limit)


def get_related_items(queryset, *, current_obj, filters=None, limit=3):
    filters = filters or {}
    related = list(queryset.filter(**filters).exclude(pk=current_obj.pk)[:limit])
    return related or list(queryset.exclude(pk=current_obj.pk)[:limit])


def get_program_location(program):
    if not program.location_name:
        return None

    site_settings = SiteSettings.load()
    if site_settings.location_name.casefold() != program.location_name.casefold():
        return None

    return site_settings


def get_program_notes(program):
    seen = set()
    notes = []
    for entry in program.schedule_entries.all():
        if not entry.notes or entry.notes in seen:
            continue

        notes.append(
            {
                "label": entry.title or entry.day_label,
                "body": entry.notes,
            }
        )
        seen.add(entry.notes)

    return notes
