from django.urls import path
from . import views

urlpatterns = [
    path('donations/', views.DonationList.as_view()),
]