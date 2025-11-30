from rest_framework import serializers
from django.apps import apps

class DonationSerializer(serializers.ModelSerializer):
    """
    Main donation serializer
    Handles both authenticated and anonymous donations
    Used for creating donations and showing full details to campaign owners
    """
    donor_name = serializers.SerializerMethodField()
    class Meta:
        model = apps.get_model('donations.Donation')
        fields = '__all__'
        read_only_fields = ('donor', 'date_donated')

    def validate(self, data):
        """
        Custom validation to handle both authenticated and anonymous donations
        If user is logged in: we use their account
        If user is NOT logged in: they must provide name and email
        """
        request = self.context.get('request')
        
        if request.user.is_authenticated:
            return data
        
        if not data.get('donor_name'):
            raise serializers.ValidationError("Name is required for anonymous donations.")
        if not data.get('donor_email'):
            raise serializers.ValidationError("Email is required for anonymous donations.")
        return data

    def get_donor_name(self, obj):
        if obj.donor: #if it's a logged in user
            return obj.donor.name
        if obj.anonymous: #if it's an anonymous donation
            return "Anonymous"
        return obj.donor_name
    
    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Donation amount must be greater than zero.")
        if value > 100000:
            raise serializers.ValidationError("Donation amount exceeds the maximum limit ($100,000).")
        return value
    
class PublicDonationSerializer(DonationSerializer):
    """
    Public donation serializer
    Hides sensitive information for public display
    """
    class Meta(DonationSerializer.Meta):
        model =  apps.get_model('donations.Donation')
        fields = ['id', 'amount', 'date_donated', 'donor_username', 'comment']

    def get_donor_name(self, obj):
        if obj.donor:
            return obj.donor.name
        if obj.anonymous:
            return "Anonymous"
        return obj.donor_name or "Anonymous"

    

class DonationDetailSerializer(DonationSerializer):
    pass