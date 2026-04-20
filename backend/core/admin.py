from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.models import Group


admin.site.site_header = "НЧ „Св. св. Кирил и Методий – 1926“"
admin.site.site_title = "Администрация"
admin.site.index_title = "Управление на съдържанието"

try:
    admin.site.unregister(Group)
except NotRegistered:
    pass
