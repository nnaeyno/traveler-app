import requests
from django.contrib.sites import requests
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView


class LoginView(TemplateView):
    template_name = "login.html"

    def get_context_data(self, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass


class RegisterView(TemplateView):
    template_name = "register.html"

    def get_context_data(self, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        pass
