import stripe
from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, permissions
from django.http import Http404, HttpResponse
from decimal import Decimal
from .stripe_service import StripeService
from .models import Donation
from campaigns.models import Campaign
from users.models import Parent, Child
from .serializers import DonationSerializer, PublicDonationSerializer

# Create your views here.
class CampaignDonationList(APIView):

    def get_object(self, pk):
        try:
            return Campaign.objects.get(pk=pk)
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
                {'detail': "This campaign is closed and no longer accepting donations."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = DonationSerializer(
            data=request.data,
            context={'request': request}
            )
        
        if serializer.is_valid():
            if request.user.is_authenticated:
                serializer.save(campaign=campaign, donor=request.user)
            else:
                serializer.save(campaign=campaign)
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
    

# === PAYMENT PROCESSING - STRIPE ===

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view(['POST'])
@permission_classes([AllowAny])
def create_donation_intent(request):
    """Create payment intent for donation"""
    try:
        campaign_id = request.data.get('campaign_id')
        amount = Decimal(request.data.get('amount'))
        donor_email = request.data.get('donor_email')
        donor_name = request.data.get('donor_name', '')

        campaign = Campaign.objects.get(id=campaign_id)
        child_id = campaign.child_id
        child = Child.objects.get(id=child_id)  
        parent_id = child.parent_id
        creator = Parent.objects.get(id=parent_id)
        
        #Create payment intent
        payment_intent = StripeService.create_payment_intent(
            amount=amount,
            campaign_id=campaign_id,
            donor_email=donor_email,
            donor_name=donor_name
        )

        #Create donation record
        donation = Donation.objects.create(
            campaign=campaign,
            amount=amount,
            donor_email=donor_email,
            donor_name=donor_name,
            stripe_payment_intent_id=payment_intent.id,
        )

        return Response({
            'client_secret': payment_intent.client_secret,
            'payment_intent_id': payment_intent.id,
            'donation_id': donation.id,
            'status': 'pending'
        })
    
    except Campaign.DoesNotExist:
        return Response({'error': 'Campaign not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    

# === WEBHOOK HANDLER ===

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def stripe_webhook(request):
    """Handle Stripe webhook events"""
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)
    
    #Handle payment intent succeeded
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']

        try:
            donation = Donation.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            donation.status = 'succeeded'
            donation.save()

            #Update campaign amount
            campaign = donation.campaign
            campaign.current_amount += donation.amount
            campaign.save()

        except Donation.DoesNotExist:
            pass

    #Handle payment intent failed
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']

        try:
            donation = Donation.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )
            donation.status = 'failed'
            donation.save()
        except Donation.DoesNotExist:
            pass

    return HttpResponse(status=200)