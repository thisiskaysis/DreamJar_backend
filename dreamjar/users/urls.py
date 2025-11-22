from django.urls import path
from . import views

urlpatterns = [
    path('parents/', views.ParentList.as_view()),
    path('parents/<int:pk>/', views.ParentDetail.as_view()),
    path('children/', views.ChildList.as_view()),
    path('children/<int:pk>/', views.ChildDetail.as_view())
]