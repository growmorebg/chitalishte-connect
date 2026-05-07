from django.conf import settings


def build_public_url(request, path=None):
    path = path or getattr(request, "path", "/") or "/"
    if not path.startswith("/"):
        path = f"/{path}"

    public_site_url = getattr(settings, "PUBLIC_SITE_URL", "").rstrip("/")
    if public_site_url:
        return f"{public_site_url}{path}"

    return request.build_absolute_uri(path)
