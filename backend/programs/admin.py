from django import forms
from django.contrib import admin
from django.utils.text import slugify

from core.admin_utils import (
    ZeroExtraTabularInline,
    build_image_preview,
)

from .models import (
    Instructor,
    PricingBlock,
    Program,
    ProgramCategory,
    ProgramGalleryImage,
    ProgramSchedule,
)


class ProgramScheduleInlineForm(forms.ModelForm):
    class Meta:
        model = ProgramSchedule
        fields = "__all__"
        labels = {
            "room": "Зала",
        }


class ProgramScheduleInline(ZeroExtraTabularInline):
    model = ProgramSchedule
    form = ProgramScheduleInlineForm
    fields = ("day_label", "start_time", "end_time", "room")


class PricingBlockInline(ZeroExtraTabularInline):
    model = PricingBlock
    fields = ("title", "price_label", "billing_period", "description")


class ProgramGalleryImageInline(ZeroExtraTabularInline):
    model = ProgramGalleryImage
    fields = ("image", "caption")
    thumbnail = build_image_preview("image", width=96, height=64)


@admin.register(ProgramCategory)
class ProgramCategoryAdmin(admin.ModelAdmin):
    change_form_template = "admin/programs/programcategory/change_form.html"
    actions = None
    list_display = ("name",)
    list_filter = ()
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "name")
    add_fieldsets = (
        (
            "Основно",
            {
                "fields": (
                    "name",
                    "description",
                )
            },
        ),
    )
    fieldsets = (
        (
            "Основно",
            {
                "fields": (
                    "name",
                    "description",
                )
            },
        ),
    )

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_prepopulated_fields(self, request, obj=None):
        return {}

    def generate_unique_slug(self, name):
        base_slug = slugify(name) or "program-category"
        slug = base_slug
        index = 2

        while ProgramCategory.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{index}"
            index += 1

        return slug

    def save_model(self, request, obj, form, change):
        if not change:
            obj.slug = obj.slug or self.generate_unique_slug(obj.name)

        super().save_model(request, obj, form, change)


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    change_form_template = "admin/programs/instructor/change_form.html"
    list_display = ("portrait_preview", "full_name", "role_title", "updated_at")
    list_filter = ()
    search_fields = ("full_name", "role_title", "biography", "credentials")
    prepopulated_fields = {"slug": ("full_name",)}
    ordering = ("full_name",)
    readonly_fields = ("portrait_preview",)
    add_fieldsets = (
        (
            "Основно",
            {
                "fields": (
                    "portrait",
                    "full_name",
                    "role_title",
                    "biography",
                    "email",
                    "phone",
                )
            },
        ),
    )
    fieldsets = add_fieldsets
    portrait_preview = build_image_preview("portrait", description="Портрет", width=72, height=72)

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_prepopulated_fields(self, request, obj=None):
        return {}

    def generate_unique_slug(self, full_name):
        max_length = Instructor._meta.get_field("slug").max_length
        base_slug = slugify(full_name) or "instructor"
        base_slug = base_slug[:max_length]
        slug = base_slug
        index = 2

        while Instructor.objects.filter(slug=slug).exists():
            suffix = f"-{index}"
            slug = f"{base_slug[: max_length - len(suffix)]}{suffix}"
            index += 1

        return slug

    def save_model(self, request, obj, form, change):
        if not change and not obj.slug:
            obj.slug = self.generate_unique_slug(obj.full_name)
        super().save_model(request, obj, form, change)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    change_form_template = "admin/programs/program/change_form.html"
    list_display = (
        "cover_preview",
        "title",
        "category",
        "inquiry_phone",
        "updated_at",
    )
    list_filter = ("category",)
    search_fields = ("title", "summary", "description", "audience", "age_group", "level", "inquiry_phone")
    filter_horizontal = ("instructors",)
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProgramScheduleInline, PricingBlockInline, ProgramGalleryImageInline]
    ordering = ("title",)
    readonly_fields = ("cover_preview",)
    add_fieldsets = (
        (
            "Основно",
            {
                "fields": (
                    "cover_image",
                    "category",
                    "title",
                    "description",
                    "instructors",
                )
            },
        ),
        (
            "Детайли за участие",
            {
                "fields": (
                    "audience",
                    "age_group",
                    "level",
                    "duration",
                    "location_name",
                    "inquiry_phone",
                )
            },
        ),
    )
    fieldsets = add_fieldsets
    cover_preview = build_image_preview("cover_image")

    def get_fieldsets(self, request, obj=None):
        if obj is None:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def get_prepopulated_fields(self, request, obj=None):
        return {}

    def generate_unique_slug(self, title):
        max_length = Program._meta.get_field("slug").max_length
        base_slug = slugify(title) or "program"
        base_slug = base_slug[:max_length]
        slug = base_slug
        index = 2

        while Program.objects.filter(slug=slug).exists():
            suffix = f"-{index}"
            slug = f"{base_slug[: max_length - len(suffix)]}{suffix}"
            index += 1

        return slug

    def generate_summary(self, program):
        summary = " ".join(program.description.split())
        return summary[:220] if summary else program.title

    def save_model(self, request, obj, form, change):
        if not change:
            obj.slug = obj.slug or self.generate_unique_slug(obj.title)
            obj.summary = obj.summary or self.generate_summary(obj)

        super().save_model(request, obj, form, change)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)

        for deleted_obj in formset.deleted_objects:
            deleted_obj.delete()

        for instance in instances:
            if isinstance(instance, PricingBlock):
                instance.is_featured = True
            instance.save()

        formset.save_m2m()

        if formset.model is PricingBlock and form.instance.pk:
            form.instance.pricing_options.update(is_featured=True)

    class Media:
        js = ("cms/js/admin_story_attachments.js",)
