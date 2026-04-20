from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse


LEGACY_CMS_ADMIN_MODEL_MAP = {
    "staticpage": ("pages", "page"),
    "page": ("pages", "page"),
    "leadershipmember": ("pages", "boardmember"),
    "boardmember": ("pages", "boardmember"),
    "galleryimage": ("pages", "galleryimage"),
    "instructor": ("programs", "instructor"),
    "program": ("programs", "program"),
    "project": ("stories", "story"),
    "story": ("stories", "story"),
    "inquirysubmission": ("inquiries", "inquirysubmission"),
}


def legacy_cms_admin_index_redirect(_request):
    return redirect("admin:index")


def legacy_cms_admin_redirect(request, model_name, suffix=""):
    target = LEGACY_CMS_ADMIN_MODEL_MAP.get(model_name.lower())
    if not target:
        raise Http404("Unknown legacy CMS admin path.")

    app_label, admin_model_name = target
    target_url = reverse(f"admin:{app_label}_{admin_model_name}_changelist")
    if suffix:
        target_url = f"{target_url}{suffix}"

    query_string = request.META.get("QUERY_STRING")
    if query_string:
        target_url = f"{target_url}?{query_string}"

    return redirect(target_url)
