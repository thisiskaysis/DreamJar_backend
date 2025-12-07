from django.urls import path
from . import views

urlpatterns = [
    path('parents/', views.ParentList.as_view()),
    path('parents/<int:pk>/', views.ParentDetail.as_view()),
    path('parents/<int:pk>/children/', views.ChildList.as_view()), 
    path('children/<int:pk>/', views.ChildDetail.as_view()),

    #Handle Google log in callback
    path('api/auth/google/callback/', views.GoogleLoginCallback.as_view(), name='google_login_landing'),

    #Stripe Connect
    path('stripe/connect/account/', views.stripe_connect_account, name='stripe_connect_account'),
    path('stripe/connect/onboarding/', views.stripe_onboarding_link, name='stripe_onboarding_link'),
    path('stripe/connect/status/', views.stripe_account_status, name='stripe_account_status'),
]