from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .models import Donation
from .serializers import DonationSerializer

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
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
            )