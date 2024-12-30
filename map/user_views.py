from django.views.generic import TemplateView


class LoginView(TemplateView):
    template_name = "login.html"

    def get_context_data(self, **kwargs):
        pass


class RegisterView(TemplateView):
    template_name = "signup.html"

    def get_context_data(self, **kwargs):
        pass
