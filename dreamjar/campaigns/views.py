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
class CampaignList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        """
        Retrieve a list of all campaigns for your own child.
        Only a Parent can view this list.
        """
        try:
            child = Child.objects.get(pk=pk)
            self.check_object_permissions(self.request, child)
            return child
        except Child.DoesNotExist:
            raise Http404
        
        if request.user != child.parent:
            return Response(
                {"detail": "You do not have permission to perform this action."},
                status=status.HTTP_403_FORBIDDEN
                )
        
        campaigns = child.owned_campaigns.all()
        serializer = CampaignSerializer(campaigns, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new campaign.
        """
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
        Retrieve a specific campaign by its ID.
        """
        campaign = self.get_object(pk)
        serializer = CampaignDetailSerializer(campaign)
        return Response(serializer.data)