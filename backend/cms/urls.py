from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import RedirectView

from . import views
from .sitemaps import sitemaps

app_name = "cms"

urlpatterns = [
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("", views.HomeView.as_view(), name="home"),
    path("programs/", views.ProgramListView.as_view(), name="programs"),
    path("programs/categories/<slug:slug>/", views.ProgramCategoryView.as_view(), name="program_category"),
    path("programs/<slug:slug>/", views.ProgramDetailView.as_view(), name="program_detail"),
    path("novini/", views.ProjectListView.as_view(), name="projects"),
    path("novini/<slug:slug>/", views.ProjectDetailView.as_view(), name="project_detail"),
    path("projects/", RedirectView.as_view(pattern_name="cms:projects", permanent=False)),
    path("projects/<slug:slug>/", RedirectView.as_view(pattern_name="cms:project_detail", permanent=False)),
    path("gallery/", views.GalleryView.as_view(), name="gallery"),
    path("contact/", views.ContactView.as_view(), name="contact"),
    path("history/", views.HistoryView.as_view(), name="history"),
    path("library/", views.LibraryView.as_view(), name="library"),
    path("библиотека/", RedirectView.as_view(pattern_name="cms:library", permanent=False)),
    path("board/", views.BoardView.as_view(), name="board"),
    path("info/<slug:slug>/", views.StaticPageView.as_view(), name="page_detail"),
    path("privacy/", views.PrivacyView.as_view(), name="privacy"),
    path("cookies/", views.CookiesView.as_view(), name="cookies"),
    path("cookies/preferences/", views.CookiePreferenceUpdateView.as_view(), name="cookie_preferences"),
    path("api/gallery/", views.gallery_api, name="api_gallery"),
    path("about/history/", RedirectView.as_view(pattern_name="cms:history", permanent=False)),
    path("about/leadership/", RedirectView.as_view(pattern_name="cms:board", permanent=False)),
    path("about/privacy/", RedirectView.as_view(pattern_name="cms:privacy", permanent=False)),
    path("about/cookies/", RedirectView.as_view(pattern_name="cms:cookies", permanent=False)),
]
