from django.urls import path
from . import views

urlpatterns = [
    path('campaigns/<int:pk>/donations/', views.CampaignDonationList.as_view()), #Public - donate here
    path('donations/', views.DonationList.as_view()),
    
    #Payment processing
    path('stripe/create-payment-intent/', views.create_donation_intent, name='create_donation_intent'),

    #Webhook
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),

]