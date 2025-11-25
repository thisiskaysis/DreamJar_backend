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

    def post(self, request):
        """
        Make a donation - with or without an account.

        1. Logged in users can make donations that are linked to their account.
        2. Anonymous users can make donations by providing their name and email.
        
        SEE IF I CAN MAKE THIS WORK:
        - User fills form
        - Submits
        - Redirected to Stripe
        - Stripe confirms donation
        - Donation saved in DB
        """
        serializer = DonationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(donor=request.user)
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )
    
class DonationDetail(APIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsDonorOrReadOnly
        ]
    """
    Retrieve, update or delete a donation instance.
    """
    def get_object(self, pk):
        try:
            donation = Donation.objects.get(pk=pk)
            self.check_object_permissions(self.request, donation)
            return donation
        except Donation.DoesNotExist:
            raise Http404