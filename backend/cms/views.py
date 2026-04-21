from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect
from django.utils import timezone
from django.views.decorators.http import require_GET
from django.views.generic import DetailView, ListView, TemplateView, View

from core.models import SiteSettings
from inquiries.notifications import send_submission_notification
from pages.models import BoardMember, GalleryImage, HistoryEntry, HomePage, LibraryImage
from programs.models import ProgramSession

from .cookies import CookiePreferences, set_cookie_preferences
from .content import PAGE_INTROS
from .forms import ContactInquiryForm, CookiePreferencesForm
from .services import (
    get_featured_programs,
    get_featured_stories,
    get_program_categories,
    get_program_location,
    get_program_notes,
    get_program_queryset,
    get_related_items,
    get_static_page,
    get_story_queryset,
)

DEFAULT_PROGRAM_CATEGORY_SLUG = "kids"
DEFAULT_PROGRAM_CATEGORY_NAME = "Деца"
ALL_PROGRAM_CATEGORIES_VALUE = "all"


class HomeView(TemplateView):
    template_name = "cms/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        home_page = HomePage.load()
        context["home_page"] = home_page
        context["home_stats"] = list(home_page.stats.all()) if home_page.pk else []
        context["home_features"] = list(home_page.features.all()) if home_page.pk else []
        context["featured_programs"] = get_featured_programs(limit=6)
        context["featured_stories"] = get_featured_stories(limit=6)
        context["program_categories"] = list(get_program_categories())
        context["upcoming_events"] = list(
            ProgramSession.objects.published().filter(date__gte=timezone.localdate())[:3]
        )
        return context


class ProgramListView(ListView):
    template_name = "cms/program_list.html"
    context_object_name = "programs"

    def get_categories(self):
        if not hasattr(self, "_program_categories"):
            self._program_categories = list(get_program_categories())
        return self._program_categories

    def get_selected_category(self):
        category_slug = self.request.GET.get("category")
        categories = self.get_categories()

        if category_slug == ALL_PROGRAM_CATEGORIES_VALUE:
            return None

        if category_slug:
            return next((category for category in categories if category.slug == category_slug), None)

        return (
            next((category for category in categories if category.slug == DEFAULT_PROGRAM_CATEGORY_SLUG), None)
            or next((category for category in categories if category.name == DEFAULT_PROGRAM_CATEGORY_NAME), None)
            or (categories[0] if categories else None)
        )

    def get_queryset(self):
        queryset = get_program_queryset()
        selected_category = self.get_selected_category()
        if selected_category:
            queryset = queryset.filter(category=selected_category)
        elif self.request.GET.get("category") and self.request.GET.get("category") != ALL_PROGRAM_CATEGORIES_VALUE:
            queryset = queryset.none()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        selected_category_obj = self.get_selected_category()
        categories = self.get_categories()
        context["page_intro"] = PAGE_INTROS["programs"]
        context["categories"] = categories
        context["selected_category"] = selected_category_obj.slug if selected_category_obj else self.request.GET.get("category", "")
        context["selected_category_obj"] = selected_category_obj
        return context


class ProgramCategoryView(DetailView):
    template_name = "cms/program_category.html"
    context_object_name = "category"
    queryset = get_program_categories()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["programs"] = (
            get_program_queryset()
            .filter(category=self.object)
            .prefetch_related("schedule_entries")
        )
        return context


class ProgramDetailView(DetailView):
    template_name = "cms/program_detail.html"
    context_object_name = "program"

    def get_queryset(self):
        return (
            get_program_queryset()
            .select_related("category")
            .prefetch_related(
                "instructors",
                "schedule_entries",
                "pricing_options",
                "gallery_items",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["related_programs"] = get_related_items(
            get_program_queryset(),
            current_obj=self.object,
            filters={"category": self.object.category},
            limit=3,
        )
        context["program_location"] = get_program_location(self.object)
        context["program_notes"] = get_program_notes(self.object)
        context["upcoming_sessions"] = list(
            ProgramSession.objects.published()
            .filter(program=self.object, date__gte=timezone.localdate())
            .order_by("date", "time")[:3]
        )
        context["site_settings"] = SiteSettings.load()
        return context


class ProjectListView(ListView):
    template_name = "cms/project_list.html"
    context_object_name = "projects"

    def get_queryset(self):
        return get_story_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_intro"] = PAGE_INTROS["projects"]
        return context


class ProjectDetailView(DetailView):
    template_name = "cms/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return get_story_queryset().prefetch_related("attachments")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["related_projects"] = get_related_items(
            get_story_queryset(),
            current_obj=self.object,
            limit=3,
        )
        return context


class GalleryView(ListView):
    template_name = "cms/gallery.html"
    context_object_name = "gallery_items"
    queryset = GalleryImage.objects.published()


class ContactView(TemplateView):
    template_name = "cms/contact.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_settings = context.get("site_settings") or SiteSettings.load()
        default_intro = PAGE_INTROS["contact"]
        context["page_intro"] = {
            "eyebrow": default_intro["eyebrow"],
            "title": site_settings.contact_page_title or default_intro["title"],
            "intro": site_settings.contact_page_intro,
        }
        context["form"] = kwargs.get("form") or ContactInquiryForm()
        return context

    def post(self, request, *args, **kwargs):
        form = ContactInquiryForm(request.POST)
        if form.is_valid():
            site_settings = SiteSettings.load()
            submission = form.save()
            send_submission_notification(submission)
            messages.success(
                request,
                site_settings.contact_page_success_message,
            )
            return redirect("cms:contact")
        return self.render_to_response(self.get_context_data(form=form))


class ManagedStaticPageView(TemplateView):
    template_name = "cms/page.html"
    page_slug = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page"] = get_static_page(self.page_slug)
        return context


class StaticPageView(TemplateView):
    template_name = "cms/page.html"
    simple_page_slugs = {"charter"}

    def get_template_names(self):
        if self.kwargs.get("slug") in self.simple_page_slugs:
            return ["cms/simple_page.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page"] = get_static_page(kwargs["slug"])
        return context


class HistoryView(ManagedStaticPageView):
    page_slug = "history"
    template_name = "cms/history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = context["page"]
        if page.pk:
            context["history_images"] = page.history_entries.published().exclude(image="")
        else:
            context["history_images"] = HistoryEntry.objects.published().filter(page__slug=self.page_slug).exclude(image="")
        return context


class LibraryView(ManagedStaticPageView):
    page_slug = "library"
    template_name = "cms/library.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = context["page"]
        if page.pk:
            context["library_images"] = page.library_images.published().exclude(image="")
        else:
            context["library_images"] = LibraryImage.objects.published().filter(page__slug=self.page_slug).exclude(image="")
        return context


class BoardView(TemplateView):
    template_name = "cms/board.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page"] = get_static_page("board")
        context["members"] = BoardMember.objects.published()
        return context


class PrivacyView(ManagedStaticPageView):
    page_slug = "privacy"
    template_name = "cms/privacy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hide_cookie_controls"] = True
        return context


class CookiesView(ManagedStaticPageView):
    page_slug = "cookies"
    template_name = "cms/cookies.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hide_cookie_controls"] = True
        return context


class CookiePreferenceUpdateView(View):
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        form = CookiePreferencesForm(request.POST)
        if not form.is_valid():
            return redirect("cms:cookies")

        preferences = CookiePreferences(
            has_choice=True,
            analytics_enabled=form.cleaned_data["analytics"],
        )
        response = redirect(form.get_redirect_to(request))
        return set_cookie_preferences(response, preferences)


@require_GET
def gallery_api(request):
    """JSON за публичната галерия — само публикувани снимки."""
    rows = []
    for item in GalleryImage.objects.published():
        if not item.image:
            continue
        image_url = request.build_absolute_uri(item.image.url)
        rows.append(
            {
                "id": item.id,
                "caption": item.caption or "",
                "image_url": image_url,
            }
        )
    response = JsonResponse({"results": rows})
    response["Access-Control-Allow-Origin"] = "*"
    return response
