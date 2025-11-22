from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .models import Campaign
from .serializers import CampaignSerializer

# Create your views here.
class CampaignList(APIView):
    def get(self, request):
        """
        Retrieve a list of all campaigns.
        """
        campaigns = Campaign.objects.all()
        serializer = CampaignSerializer(campaigns, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new campaign.
        """
        serializer = CampaignSerializer(data=request.data)
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
    
class CampaignDetail(APIView):
    def get_object(self, pk):
        try:
            campaign = Campaign.objects.get(pk=pk)
            return campaign
        except Campaign.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """
        Retrieve a specific campaign by its ID.
        """
        campaign = self.get_object(pk)
        serializer = CampaignSerializer(campaign)
        return Response(serializer.data)