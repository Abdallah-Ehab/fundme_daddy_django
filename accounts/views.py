from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views import View

from .forms import RegistrationForm, LoginForm


class RegisterView(View):
    form_class = RegistrationForm
    template_name = "accounts/register.html"

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST)
        if form.is_valid():
            form.save()
            return redirect("accounts:registration_done")
        return render(request, self.template_name, {"form": form})


class CustomLoginView(LoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"

    def form_valid(self, form):
        messages.success(self.request, "Logged in successfully.")
        return super().form_valid(form)


def registration_done(request):
    return render(request, "accounts/registration_done.html")


class CustomLogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, "Logged out successfully.")
        return redirect("accounts:login")
