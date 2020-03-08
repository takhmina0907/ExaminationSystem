from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import (
    LoginView as BaseLoginView, LogoutView as BaseLogoutView)

from things.admin_forms.forms import UserCreateForm, UserAuthForm


class RegistrationView(CreateView):
    form_class = UserCreateForm
    template_name = 'admin/registration.html'
    # TODO change reverse lazy path
    success_url = reverse_lazy('home')


class LoginView(BaseLoginView):
    form_class = UserAuthForm
    template_name = 'admin/login.html'
    # TODO change reverse lazy path
    success_url = reverse_lazy('home')

    def get_success_url(self):
        return self.success_url


# TODO test logout
class LogoutView(BaseLogoutView):
    def get_next_page(self):
        # TODO change reverse lazy path
        return reverse_lazy('home')
