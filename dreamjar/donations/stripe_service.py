import stripe
from django.conf import settings
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY

class StripeService:

    # ==== Simple Payment Collection (No Connect needed initially) ====

    @staticmethod
    def create_payment_intent(amount, campaign_id, donor_email, donor_name=''):
        """Create simple payment intent - money goes to platform account"""
        payment_intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),
            currency='aud',
            payment_method_types=['card'],
            metadata={
                'campaign_id': str(campaign_id),
                'donor_email': donor_email,
                'donor_name': donor_name,
            },
        )
        return payment_intent
    
    # ==== Simplified Australian Creator onboarding ====

    @staticmethod
    def create_custom_account(email):
        account = stripe.Account.create(
            type='custom',
            country='AU',
            email=email,
            capabilities={
                'transfers': {'requested': True},
            },
            business_type='individual'
        )
        return account.id
    
    @staticmethod
    def update_account_details(account_id, first_name, last_name, dob, address_line1, city, state, postal_code, ip_address):
        """Update account with Australian identity verification"""
        try:
            stripe.Account.modify(
                account_id,
                individual={
                    'first_name': first_name,
                    'last_name': last_name,
                    'dob': {
                        'day': dob['day'],
                        'month': dob['month'],
                        'year': dob['year'],
                    },
                    'address': {
                        'line1': address_line1,
                        'city': city,
                        'state': state,
                        'postal_code': postal_code,
                        'country': 'AU',
                    }
                },
                tos_acceptance={
                    'date': int(stripe.util.convert_to_stripe_object(stripe.util.now(), None)),
                    'ip': ip_address,
                },
            )
            return True
        except Exception as e:
            raise Exception(f"Failed to update account: {str(e)}")
        
    def add_bank_account(account_id, bsb, account_number, account_holder_name):
        """Add Australian bank account for payouts"""
        try:
            # Create bank account token
            token = stripe.Token.create(
                bank_account={
                    'country': 'AU',
                    'currency': 'aud',
                    'account_holder_name': account_holder_name,
                    'account_holder_type': 'individual',
                    'routing_number': bsb,
                    'account_number': account_number
                }
            )

            # Add to Connect account
            external_account = stripe.Account.create_external_account(
                account_id,
                external_account=token.id,
            )

            return external_account.id
        except Exception as e:
            raise Exception(f"Failed to add bank account: {str(e)}")
        
    @staticmethod
    def check_account_status(accound_id):
        """Check if account is ready to receive payouts"""
        account = stripe.Account.retrieve(accound_id)
        return account.payouts_enabled
    
    # === Payout/Transfer to creators ====

    @staticmethod
    def transfer_to_creator(account_id, amount, campaign_id, description=''):
        """Transfer funds from platform to creator's account"""
        try:
            transfer = stripe.Transfer.create(
                amount=int(amount * 100),
                currency='aud',
                destination=account_id,
                description=description or f'Payout for campaign {campaign_id}',
                metadata={
                    'campaign_id': str(campaign_id)
                },
            )
            return transfer
        except Exception as e:
            raise Exception(f"Transfer failed: {str(e)}")