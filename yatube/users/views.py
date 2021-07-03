from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView

from .forms import CreationForm


class SignUp(CreateView):
    form_class = CreationForm
    success_url = reverse_lazy('login')
    template_name = 'users/signup.html'


LoginView.template_name = 'users/login.html'
