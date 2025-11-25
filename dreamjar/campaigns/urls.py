from django.urls import path
from . import views

urlpatterns = [
    path('campaigns/', views.PublicCampaignList.as_view()),
    path('campaigns/<int:pk>/', views.CampaignDetail.as_view()),
    path('children/<int:pk>/campaigns/', views.ChildCampaignList.as_view()),
]