from django.urls import path
from . import views

urlpatterns = [
    path('campaigns/', views.CampaignList.as_view()),
]