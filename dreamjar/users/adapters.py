from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.signals import social_account_updated, social_account_added
from django.dispatch import receiver

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        user = super().save_user(request, sociallogin, form)
        return user

    def get_connect_redirect_url(self, request, socialaccount):
        return '/api/auth/google/callback/'