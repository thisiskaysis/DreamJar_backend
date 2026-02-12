from django.urls import path
from . import views

urlpatterns = [
    path('campaigns/', views.PublicCampaignList.as_view()), #Public - browse all
    path('campaigns/<int:pk>/', views.CampaignDetail.as_view()), #Public - GET, Owner, PUT/DELETE
    path('children/<int:pk>/campaigns/', views.ChildCampaignList.as_view()),
    path('accounts/profile/', views.PublicCampaignList.as_view()), #THIS IS A HACK - we want to redirect to the public campaign list, but we need to have a URL that matches the default login redirect URL for Google
]