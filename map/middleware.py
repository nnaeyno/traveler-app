import jwt
from django.http import HttpResponse
from django.shortcuts import redirect

from roadrunner import settings


class AuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        public_paths = ['/login/', '/api/login/']

        if any(request.path.startswith(path) for path in public_paths):
            return self.get_response(request)

        access_token = request.session.get('access_token')

        if not access_token:
            if request.path.startswith('/api/'):
                return HttpResponse('Unauthorized', status=401)
            return redirect('traveler:login')

        try:
            payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=["HS256"])
            request.user = payload  # Optional: Attach user data from the token
        except jwt.ExpiredSignatureError:
            del request.session['access_token']
            if request.path.startswith('/api/'):
                return HttpResponse('Unauthorized', status=401)
            return redirect('traveler:login')
        except jwt.InvalidTokenError:

            del request.session['access_token']
            if request.path.startswith('/api/'):
                return HttpResponse('Unauthorized', status=401)
            return redirect('traveler:login')

        # Add token to request headers for API calls
        request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'

        return self.get_response(request)

    """
    curl -X GET "http://127.0.0.1:8000/api/cities/" -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM1NjQyMTQyLCJpYXQiOjE3MzU2Mzg1NDIsImp0aSI6IjY1N2I0OTQxOGU3YTQ2MmY4MjFkMDI1NDU0NzNhZjA1IiwidXNlcl9pZCI6Mn0.CFG6ovwe5EuF8PJigxNRciG9kSDFe_45VGBfBX2SLi4" 
    
    curl -X GET "http://127.0.0.1:8000/api/cities/" \
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM1NjQyNDU2LCJpYXQiOjE3MzU2Mzg4NTYsImp0aSI6IjEzNjFjYWU2MjJiMDQyZTdiZDQ0NzViZjI2ODAyOGZkIiwidXNlcl9pZCI6MX0.FTGg5GkaATMYhyaW8z3J7_k14tjdhlqjDeC_971-X1Y"    """