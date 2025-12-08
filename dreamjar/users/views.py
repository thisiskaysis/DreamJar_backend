from django.shortcuts import render
from django.http import Http404
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework import status, permissions
import stripe
from donations.stripe_service import StripeService
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
        
        active_campaigns = child.owned_campaigns.filter(is_open=True).count()
        if active_campaigns > 0:
            return Response(
                {'detail': "Cannot delete child with active campaigns."},
                status=status.HTTP_400_BAD_REQUEST
            )
        child.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

# === GOOGLE CALLBACK ===
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
            return Response(
                {
                    'error': 'Authentication failed',
                    'detail': 'User not authenticated after OAuth callback'
                }, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": {
                "id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "username": user.username
            },
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        })
    
# === STRIPE CONNECT ===

stripe.api_key = settings.STRIPE_SECRET_KEY

@api_view({'POST'})
@permission_classes([IsAuthenticated])
def setup_payout_account(request):
    try:
        user = request.user

        # Create Stripe account if it doesn't exist
        if not user.stripe_account_id:
            account_id = StripeService.create_custom_account(user.email)
            user.stripe_account_id = account_id
            user.save()

        # Update account with personal details
        StripeService.update_account_details(
            account_id=user.stripe_account_id,
            first_name=request.data.get('first_name'),
            last_name=request.data.get('last_name'),
            dob=request.data.get('dob'),
            address_line1=request.data.get('address_line1'),
            city=request.data.get('city'),
            state=request.data.get('state'),
            postal_code=request.data.get('postal_code'),
            ip_address=request.META.get('REMOTE_ADDR', '0.0.0.0'),
        )

        return Response({
            'message': 'Personal details saved',
            'account_id': user.stripe_account_id,
            'next_step': 'add_bank_account'
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_bank_details(request):
    """
    Add Australian bank account
    Required fields:
    - bsb (6 digits)
    - account_number
    - account_holder_name
    """
    try:
        user = request.user

        if not user.stripe_account_id:
            return Response(
                {'error': 'Please complete personal details first'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        #Add bank account
        StripeService.add_bank_account(
            account_id=user.stripe_account_id,
            bsb=request.data.get('bsb'),
            account_number=request.data.get('account_number'),
            account_holder_name=request.data.get('account_holder_name'),
        )

        #Check if account is ready
        is_ready = StripeService.check_account_status(user.stripe_account_id)
        user.stripe_onboarding_complete = is_ready
        user.save()

        return Response({
            'message': 'Bank account added successfully',
            'onboarding_complete': is_ready,
            'pending_balance': str(user.pending_balance)
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)