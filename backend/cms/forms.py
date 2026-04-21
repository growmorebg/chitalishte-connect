from django import forms
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from inquiries.models import InquirySubmission, InquiryType


class ContactInquiryForm(forms.ModelForm):
    consent = forms.BooleanField(
        label="Съгласен/на съм данните ми да бъдат използвани за отговор на запитването.",
        error_messages={"required": "Необходимо е съгласие, за да изпратим отговор."},
    )

    class Meta:
        model = InquirySubmission
        fields = ["full_name", "email", "phone", "subject", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }
        labels = {
            "full_name": "Име и фамилия",
            "email": "Имейл",
            "phone": "Телефон",
            "subject": "Тема",
            "message": "Съобщение",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["subject"].initial = "Общо запитване"
        self.fields["full_name"].widget.attrs.update(
            {
                "placeholder": "Вашето име",
                "autocomplete": "name",
                "autofocus": True,
            }
        )
        self.fields["email"].widget.attrs.update(
            {
                "placeholder": "Вашият e-mail адрес",
                "autocomplete": "email",
                "inputmode": "email",
            }
        )
        self.fields["phone"].widget.attrs.update(
            {
                "placeholder": "Вашият телефонен номер",
                "autocomplete": "tel",
                "inputmode": "tel",
            }
        )
        self.fields["subject"].widget.attrs.update(
            {
                "placeholder": "Тема",
                "autocomplete": "off",
            }
        )
        self.fields["message"].widget.attrs.update(
            {
                "rows": 6,
                "placeholder": "Съобщение",
            }
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.inquiry_type = InquiryType.GENERAL
        if commit:
            instance.save()
        return instance


class EnrollmentInquiryForm(forms.ModelForm):
    consent = forms.BooleanField(
        label="Съгласен/на съм данните ми да бъдат използвани за обратна връзка.",
        error_messages={"required": "Необходимо е съгласие, за да изпратим отговор."},
    )

    class Meta:
        model = InquirySubmission
        fields = ["full_name", "email", "phone", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }
        labels = {
            "full_name": "Име и фамилия",
            "email": "Имейл",
            "phone": "Телефон",
            "message": "Какво бихте искали да попитате",
        }

    def save(self, commit=True, *, program):
        instance = super().save(commit=False)
        instance.inquiry_type = InquiryType.ENROLLMENT
        instance.program = program
        instance.subject = f"Записване за {program.title}"
        if commit:
            instance.save()
        return instance


class CookiePreferencesForm(forms.Form):
    analytics = forms.BooleanField(
        required=False,
        label="Разрешавам анонимни аналитични бисквитки.",
    )
    redirect_to = forms.CharField(required=False, widget=forms.HiddenInput)

    def get_redirect_to(self, request):
        redirect_to = self.cleaned_data.get("redirect_to") or reverse("cms:cookies")
        if url_has_allowed_host_and_scheme(
            redirect_to,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return redirect_to
        return reverse("cms:cookies")
