from django.urls import path
from . import views

urlpatterns = [
    path('donations/', views.DonationList.as_view()),
    path('donations/<int:pk>/', views.DonationDetail.as_view()),
]