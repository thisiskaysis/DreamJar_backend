from django.urls import path
from . import views

urlpatterns = [
    path('campaigns/', views.PublicCampaignList.as_view()), #Public - browse all
    path('campaigns/<int:pk>/', views.CampaignDetail.as_view()), #Public - GET, Owner, PUT/DELETE
    path('children/<int:pk>/campaigns/', views.ChildCampaignList.as_view()), #Parents manage child's campaigns here
]