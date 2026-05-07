from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from pages.models import Page
from programs.models import Program, ProgramCategory
from stories.models import Story

from .content import DISABLED_PAGE_SLUGS
from .services import get_story_queryset


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"

    def items(self):
        return [
            "cms:home",
            "cms:programs",
            "cms:projects",
            "cms:gallery",
            "cms:contact",
            "cms:history",
            "cms:library",
            "cms:board",
            "cms:privacy",
            "cms:cookies",
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        return 1.0 if item == "cms:home" else 0.7


class PageSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        routed_slugs = {"history", "library", "board", "leadership", "privacy", "cookies"}
        return Page.objects.published().exclude(slug__in=routed_slugs | set(DISABLED_PAGE_SLUGS))

    def lastmod(self, item):
        return item.updated_at


class ProgramCategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return ProgramCategory.objects.published()


class ProgramSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Program.objects.published()

    def lastmod(self, item):
        return item.updated_at


class StorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return get_story_queryset()

    def lastmod(self, item):
        return item.published_at


sitemaps = {
    "static": StaticViewSitemap,
    "pages": PageSitemap,
    "program_categories": ProgramCategorySitemap,
    "programs": ProgramSitemap,
    "stories": StorySitemap,
}
