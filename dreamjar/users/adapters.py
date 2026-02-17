from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def get_login_redirect_url(self, request):
        return '/api/auth/google/callback/'
    
    def get_connect_redirect_url(self, request, socialaccount):
        return 'api/auth/google/callback/'