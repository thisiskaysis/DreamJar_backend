from django.urls import path
from . import views

urlpatterns = [
    path('parents/', views.ParentList.as_view()), #POST only
    path('parents/<int:pk>/', views.ParentDetail.as_view()), #GET User
    path('parents/<int:pk>/children/', views.ChildList.as_view()), #List children under parents
    path('children/<int:pk>/', views.ChildDetail.as_view()), #GET/PUT/DELETE specific child
]