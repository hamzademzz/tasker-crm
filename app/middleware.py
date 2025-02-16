from django.shortcuts import redirect
from django.urls import reverse

class AdminRestrictionMiddleware:
    """
    Middleware that restricts non-admin users from accessing the admin page.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the user is trying to access the /admin path
        if request.path.startswith('/admin/') and request.user.username != 'admin':
            return redirect('tasker')  # Redirect non-admins to the tasker page (or another URL)

        response = self.get_response(request)
        return response
