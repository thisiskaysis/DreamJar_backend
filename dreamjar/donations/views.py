from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import Http404
from .permissions import IsDonorOrReadOnly
from .models import Donation
from campaigns.models import Campaign
from .serializers import DonationSerializer, PublicDonationSerializer, DonationDetailSerializer

# Create your views here.
class CampaignDonationList(APIView):

    def get_object(self, pk):
        try:
            campaign = Campaign.objects.get(pk=pk)
            self.check_object_permissions(self.request, campaign)
            return campaign
        except Campaign.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        campaign = self.get_object(pk)
        donations = campaign.donations.all()
        serializer = PublicDonationSerializer(donations, many=True)
        return Response(serializer.data)

    def post(self, request, pk):
        """
        Make a donation - with or without an account.
        1. Logged in users can make donations that are linked to their account.
        2. Anonymous users can make donations by providing their name and email.
        """
        campaign = self.get_object(pk)

        if not campaign.is_open:
            return Response(
                {'detail': "This campaign is closed and no longer accepting donations."}
            )
        
        #Add campaign to data - I think this is what I need here if I want Stripe to work, bc data will come from Stripe?
        data = request.data.copy()
        data['campaign'] = campaign.id

        serializer = DonationSerializer(data=request.data)
        if serializer.is_valid():
            if request.user.is_authenticated:
                serializer.save(donor=request.user)
            else:
                serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )
    
class DonationList(APIView):
    """
    View donations you have made (authenticated users only)
    """
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        donations = Donation.objects.filter(donor=request.user)
        serializer = DonationSerializer(donations, many=True)
        return Response(serializer.data)