from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Project, Donation, Category, Tag


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["title", "image", "category", "tags", "details", "total_target", "start_time", "end_time"]
        widgets = {
            "start_time": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}, format="%Y-%m-%dT%H:%M"),
            "end_time": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}, format="%Y-%m-%dT%H:%M"),
            "details": forms.Textarea(attrs={"rows": 5, "class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "total_target": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["tags"].queryset = Tag.objects.all()
        self.fields["category"].queryset = Category.objects.all()
        self.fields["category"].empty_label = "-- Select a category --"
        if not self.instance.pk:
            now = timezone.now()
            self.fields["start_time"].initial = (now + timezone.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
            self.fields["end_time"].initial = (now + timezone.timedelta(days=30)).strftime("%Y-%m-%dT%H:%M")

    def clean_total_target(self):
        value = self.cleaned_data.get("total_target")
        if value is not None and value <= 0:
            raise ValidationError("Total target must be a positive number.")
        return value

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time:
            if end_time <= start_time:
                raise ValidationError("End time must be after start time.")
            if not self.instance.pk and start_time < timezone.now():
                raise ValidationError("Start time cannot be in the past.")
        return cleaned_data


class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = ["amount", "message"]
        widgets = {
            "amount": forms.NumberInput(attrs={"class": "form-control", "step": "0.01", "min": "1"}),
            "message": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Leave a message (optional)"}),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get("amount")
        if amount is not None and amount <= 0:
            raise ValidationError("Amount must be positive.")
        return amount
