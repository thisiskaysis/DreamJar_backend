from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status, permissions
from .models import Parent, Child
from .serializers import ParentSerializer, ChildSerializer

# Create your views here.
class ParentList(APIView):
    """
    Registration only - no GET method
    No browsing of parents as campaigns will be linked to children
    """
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        """Registration - returns JWT token immediately after signup"""
        serializer = ParentSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            #Generate JWT token for immediate login
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': serializer.data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )
    
class ParentDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Parent.objects.get(pk=pk)
        except Parent.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        parent = self.get_object(pk)
        if request.user != parent:
            return Response(
                {'detail': "You don't have permission to view this profile."},
                status=status.HTTP_403_FORBIDDEN
                )
        serializer = ParentSerializer(parent)
        return Response(serializer.data)
    
    def put(self, request, pk):
        parent = self.get_object(pk)
        if request.user != parent:
            return Response(
                {'detail': "You don't have permission to edit this profile."},
                status=status.HTTP_403_FORBIDDEN
                )
        serializer = ParentSerializer(parent, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )
        
    def delete(self, request, pk):
        parent = self.get_object(pk)
    
        if request.user != parent:
            return Response(
                {"detail": "You don't have permission to delete this account."},
                status=status.HTTP_403_FORBIDDEN
            )
            
        parent.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ChildList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_parent(self, pk):
        try:
            return Parent.objects.get(pk=pk)
        except Parent.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        parent = self.get_parent(pk)

        if request.user != parent:
            return Response(
                {'detail': "You don't have permission to view these children."},
                status=status.HTTP_403_FORBIDDEN
            )

        children = parent.children.all()
        serializer = ChildSerializer(children, many=True)
        return Response(serializer.data)
    
    def post(self, request, pk):
        parent = self.get_parent(pk)

        if request.user != parent:
            return Response(
                {'detail': "You can only create children for yourself."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ChildSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )
    
class ChildDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Child.objects.get(pk=pk)
        except Child.DoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None):
        child = self.get_object(pk)

        if request.user != child.parent:
            return Response(
                {'detail': "You don't have permission to view this child."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ChildSerializer(child)
        return Response(serializer.data)
    
    def put(self, request, pk):
        child = self.get_object(pk)

        if request.user != child.parent:
            return Response(
                {'detail': "You don't have permission to edit this child."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ChildSerializer(child, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )
    
    def delete(self, request, pk):
        child = self.get_object(pk)

        if request.user != child.parent:
            return Response(
                {"detail": "You don't have permission to delete this child."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        active_campaigns = child.campaigns.filter(is_open=True).count()
        if active_campaigns > 0:
            return Response(
                {'detail': "Cannot delete child with active campaigns."},
                status=status.HTTP_400_BAD_REQUEST
            )
        child.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class GoogleLoginCallback(APIView):
    """
    Handle Google OAuth callback.
    Returns JWT + user info as JSON.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        #User should be authenticated by allauth at this point
        user = request.user
        
        if not user.is_authenticated:
            return redirect(f"https://dreamjar.netlify.app/login?error=oauth_failed")

        
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        redirect_url = (
            f"https://dreamjar.netlify.app/oauth/google/callback?"
            f"access={access_token}&refresh={refresh_token}&login_success=true"
        )

        return redirect(redirect_url)
    
class CurrentUserView(APIView):
    """Returns the currently logged-in user based on JWT token"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        parent = request.user
        serializer = ParentSerializer(parent)
        return Response(serializer.data, status=status.HTTP_200_OK)