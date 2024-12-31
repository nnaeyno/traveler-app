from django.http import HttpResponseRedirect
from django.urls import reverse


class JWTLoginRequiredMixin:
    """Custom mixin to check for access token in session."""

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('access_token'):
            return HttpResponseRedirect(reverse('traveler:login'))
        return super().dispatch(request, *args, **kwargs)
