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

stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.
class CampaignDonationList(APIView):
    """
    GET: List all donations for a specific campaign (public)
    POST: Create payment intent to donate to a specific campaign
    """
    permission_classes = [AllowAny]

    def get_object(self, pk):
        try:
            return Campaign.objects.get(pk=pk)
        except Campaign.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        """List all successful donations for a campaign"""
        campaign = self.get_object(pk)
        donations = campaign.donations.filter(status='succeeded').order_by('-created_at')
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
        
        # Extract donation data from request
        amount = request.data.get('amount')
        comment = request.data.get('comment', '')
        anonymous = request.data.get('anonymous', False)

        # Validate amount
        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise Response(
                    {'detail': "Amount must be greater than zero."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if amount > 100000:
                return Response(
                    {'detail': "Amount exceeds maximum limit ($100,000)."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (TypeError, ValueError):
            return Response(
                {'detail': "Invalid amount."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Determine donor info
        if request.user.is_authenticated:
            donor = request.user
            donor_email = donor.email
            donor_name = f"{donor.first_name} {donor.last_name}".strip()
        else:
            donor = None
            donor_email = request.data.get('donor_email')
            donor_name = request.data.get('donor_name', '')

            if not donor_email or not donor_name:
                return Response(
                    {'detail': "Name and email are required for anonymous donations."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
        try:
            # Create Stripe Payment Intent
            payment_intent = StripeService.create_payment_intent(
                amount=amount,
                campaign_id=campaign.id,
                donor_email=donor_email,
                donor_name=donor_name
            )

            donation = Donation.objects.create(
                campaign=campaign,
                amount=amount,
                donor=donor,
                donor_email=donor_email,
                donor_name=donor_name,
                stripe_payment_intent_id=payment_intent.id,
                comment=comment,
                anonymous=anonymous,
                status='pending'
            )

            return Response({
                'client_secret': payment_intent.client_secret,
                'payment_intent_id': payment_intent.id,
                'donation_id': donation.id,
                'message': 'Payment intent created. Complete payment on frontend.'
            }, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
class DonationList(APIView):
    """
    View donations you have made (authenticated users only)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        donations = Donation.objects.filter(donor=request.user)
        serializer = DonationSerializer(donations, many=True)
        return Response(serializer.data)

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
    
    #Handle payment success
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']

        try:
            donation = Donation.objects.get(
                stripe_payment_intent_id=payment_intent['id']
            )

            # Update donation status
            donation.status = 'succeeded'
            donation.save()

            #Update campaign total (only on success)
            campaign = donation.campaign
            campaign.current_amount += donation.amount
            campaign.save()

            #Update parent's pending balance
            child = campaign.child
            parent = child.parent
            parent.pending_balance += donation.amount
            parent.save()

        except Donation.DoesNotExist:
            pass

    #Handle payment failure
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
