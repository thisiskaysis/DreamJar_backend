import stripe
from django.conf import settings
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:

    @staticmethod
    def create_connect_account(email):
        """Create Stripe Connect Express account for campaign owner"""
        account = stripe.Account.create(
            type='express',
            country='AU',
            email=email,
            capabilities={
                'card_payments': {'requested': True},
                'transfers': {'requested': True},
            }
        )
        return account.id
    
    @staticmethod
    def create_onboarding_link(account_id, refresh_url, return_url):
        """Generate onboarding link for Connect account setup"""
        account_link = stripe.AccountLink.create(
            account=account_id,
            refresh_url=refresh_url,
            return_url=return_url,
            type='account_onboarding',
        )
        return account_link.url
    
    @staticmethod
    def check_account_status(account_id):
        """Check if Connect account onboarding is complete"""
        account = stripe.Account.retrieve(account_id)
        return account.charges_enabled and account.payouts_enabled
    
    @staticmethod
    def create_payment_intent(amount, campaign_creator_stripe_account, metadata=None):
        """
        Create payment intent with destination charge (direct charge to connected account)
        Amount should be in cents (multiply by 100)
        """
        platform_fee = int(amount * Decimal('0.01')) #1% platform fee

        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency='aud',
            payment_method_types=['card'],
            application_fee_amount=platform_fee,
            transfer_data={
                'destination': campaign_creator_stripe_account
            },
            metadata=metadata or {},
        )
        return payment_intent
    
    @staticmethod
    def confirm_payment_intent(payment_intent_id):
        """Retrieve payment intent status"""
        return stripe.PaymentIntent.retrieve(payment_intent_id)