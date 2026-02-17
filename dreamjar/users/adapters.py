from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        """
        After successful OAuth login, redirect to JWT token endpoint
        """
        return '/api/auth/google/callback/'