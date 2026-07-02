from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Sum, Count, Q
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView

from accounts.models import User
from .forms import ProjectForm, DonationForm
from .models import Project, Donation, Category


def home(request):
    featured_projects = Project.objects.filter(end_time__gte=timezone.now()).order_by("-created_at")[:6]
    total_raised = Donation.objects.aggregate(total=Sum("amount"))["total"] or 0
    total_projects = Project.objects.count()
    total_donors = Donation.objects.values("donor").distinct().count()
    context = {
        "featured_projects": featured_projects,
        "total_raised": total_raised,
        "total_projects": total_projects,
        "total_donors": total_donors,
    }
    return render(request, "home.html", context)


def about(request):
    return render(request, "about.html")


class ProjectListView(ListView):
    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    ordering = ["-created_at"]

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        category = self.request.GET.get("category")
        date = self.request.GET.get("date")
        start = self.request.GET.get("start")
        end = self.request.GET.get("end")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(details__icontains=q))
        if category:
            qs = qs.filter(category__slug=category)
        if date:
            qs = qs.filter(start_time__lte=date, end_time__gte=date)
        if start:
            qs = qs.filter(start_time__gte=start)
        if end:
            qs = qs.filter(end_time__lte=end)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.objects.all()
        return context


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/project_detail.html"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["donation_form"] = DonationForm()
        context["donations"] = self.object.donations.select_related("donor").order_by("-created_at")[:20]
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_authenticated:
            return redirect(f"{reverse_lazy('accounts:login')}?next={request.path}")
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.project = self.object
            donation.donor = request.user
            donation.save()
            self.object.current_amount += donation.amount
            self.object.save(update_fields=["current_amount"])
            messages.success(request, f"Thank you! You donated ${donation.amount} to {self.object.title}.")
        else:
            messages.error(request, "Invalid donation amount.")
        return redirect("projects:detail", pk=self.object.pk)


class ProjectCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"
    success_url = reverse_lazy("projects:list")
    success_message = "Project created successfully."

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        project = self.get_object()
        return project.owner == self.request.user


class ProjectUpdateView(LoginRequiredMixin, OwnerRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"
    success_message = "Project updated successfully."

    def get_success_url(self):
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.pk})


class ProjectDeleteView(LoginRequiredMixin, OwnerRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Project
    template_name = "projects/project_confirm_delete.html"
    success_url = reverse_lazy("projects:list")
    success_message = "Project deleted successfully."


class UserDirectoryView(ListView):
    model = User
    template_name = "users/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        return User.objects.filter(
            projects__isnull=False, is_active=True
        ).annotate(
            project_count=Count("projects"),
            total_raised=Sum("projects__current_amount"),
        ).distinct().order_by("-total_raised")


class UserDetailView(DetailView):
    model = User
    template_name = "users/user_detail.html"
    context_object_name = "profile_user"

    def get_queryset(self):
        return User.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["user_projects"] = self.object.projects.all().order_by("-created_at")
        return context
