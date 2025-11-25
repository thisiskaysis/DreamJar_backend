from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import Http404
from .permissions import IsOwnerOrReadOnly
from .models import Campaign
from .serializers import CampaignSerializer, PublicCampaignSerializer, CampaignDetailSerializer
from users.models import Child

# Create your views here. 
class ChildCampaignList(APIView):
    """
    For campaigns related to a specific child.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            child = Child.objects.get(pk=pk)
            self.check_object_permissions(self.request, child)
            return child
        except Child.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """
        Retrieve a list of all campaigns for your child.
        Only a Parent can view this list.
        """
        child = self.get_object(pk)
        campaigns = child.campaigns.all()
        serializer = CampaignSerializer(campaigns, many=True)
        
        if request.user != child.parent:
            return Response(
                {"detail": "You do not have permission to view these DreamJars."},
                status=status.HTTP_403_FORBIDDEN
                )
        
        return Response(serializer.data)

    def post(self, request, pk):
        """
        Create a new campaign for your child.
        """
        child = self.get_object(pk)
        
        if request.user != child.parent:
            return Response(
                {"detail": "You do not have permission to create a DreamJar for this child."},
                status=status.HTTP_403_FORBIDDEN
                )
        
        serializer = CampaignSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(child=request.user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )
    
class PublicCampaignList(APIView):
    """
    Anyone can view and browse campaigns
    """
    def get(self, request):
        campaigns = Campaign.objects.filter(is_open=True)
        serializer = PublicCampaignSerializer(campaigns, many=True)
        return Response(serializer.data)
    
class CampaignDetail(APIView):

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
        ]
    
    def get_object(self, pk):
        try:
            campaign = Campaign.objects.get(pk=pk)
            self.check_object_permissions(self.request, campaign)
            return campaign
        except Campaign.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """
        Parent (User) can view detailed info
        Public can view limited info
        """
        campaign = self.get_object(pk)

        if request.user == campaign.child.parent:
            serializer = CampaignDetailSerializer(campaign)
        else:
            serializer = PublicCampaignSerializer(campaign)
        return Response(serializer.data)
    
    def put(self, request, pk):
        """
        Parent (User) can update their child's campaign
        """
        campaign = self.get_object(pk)
        serializer = CampaignDetailSerializer(
            instance=campaign,
            data=request.data,
            partial=True
            )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )
    
    def delete(self, request, pk):
        """
        Parent (User) can delete their child's campaign
        """
        campaign = self.get_object(pk)
        campaign.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)