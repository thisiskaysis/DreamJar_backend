from django.urls import path
from . import views

urlpatterns = [
    path('parents/', views.ParentList.as_view()),
    path('parents/<int:pk>/', views.ParentDetail.as_view()),
    path('parents/<int:pk>/children/', views.ChildList.as_view()), 
    path('children/<int:pk>/', views.ChildDetail.as_view()),

    #Handle Google log in callback
    path('api/auth/google/callback/', views.GoogleLoginCallback.as_view(), name='google_login_landing'),

    # Stripe Payout Setup
    path('payout/setup/', views.setup_payout_account, name='setup_payout'),
    path('payout/add-bank/', views.add_bank_details, name='add_bank_details'),
    path('payout/status/', views.payout_status, name='payout_status'),
    path('payout/request/', views.request_payout, name='request_payout')
]