from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .models import Donation
from .serializers import DonationSerializer, DonationDetailSerializer
from campaigns.models import Campaign
from campaigns.serializers import CampaignSerializer, CampaignDetailSerializer

# Create your views here.
class DonationList(APIView):
    """
    List all donations or create a new donation.
    """
    def get(self, request):
        donations = Donation.objects.all()
        serializer = DonationSerializer(donations, many=True)
        return Response(serializer.data)

    def post(self, request):
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

    def put(self, request, pk):
        donation = self.get_object(pk)
        serializer = DonationDetailSerializer(
            instance=donation,
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