from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
import requests
from django.contrib import messages
from map.forms import LoginForm
from user.models import User


class LoginView(View):
    template_name = 'login.html'
    home_page = 'city.html'

    def get(self, request):
        form = LoginForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            response = requests.post(
                'http://127.0.0.1:8000/api/login/',
                data={
                    'identifier': username,
                    'password': password
                }
            )

            if response.status_code == 200:
                data = response.json()
                print("Login response:", data)
                token = data["tokens"]["access"]
                if token:
                    request.session['access_token'] = token
                    return redirect('traveler:map')
            else:
                print("Login failed:", response.text)  # Debug login failure
                messages.error(request, 'Invalid credentials')

        return render(request, self.template_name, {'form': form})


class RegisterView(TemplateView):
    template_name = "signup.html"

    def get_context_data(self, **kwargs):
        pass
