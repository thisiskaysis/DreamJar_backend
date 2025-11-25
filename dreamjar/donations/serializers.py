from rest_framework import serializers
from django.apps import apps

class DonationSerializer(serializers.ModelSerializer):
    """
    Main donation serializer
    Handles both authenticated and anonymous donations
    Used for creating donations and showing full details to campaign owners
    """
    donor_username = serializers.SerializerMethodField()
    class Meta:
        model = apps.get_model('donations.Donation')
        fields = '__all__'
        read_only_fields = ('donor', 'date_donated')

    def get_donor_username(self, obj):
        if obj.donor: #if it's a logged in user
            return obj.donor.username
        return obj.donor_name or "Anonymous"
    
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

    # HOW TO MAKE ANONYMOUS DONATIONS HIDE DONOR NAME

class DonationDetailSerializer(DonationSerializer):
    pass