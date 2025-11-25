from django.urls import path
from . import views

urlpatterns = [
    path('campaigns/<int:pk>/donations/', views.CampaignDonationList.as_view()),
    path('donations/<int:pk>/', views.DonationDetail.as_view()),
]