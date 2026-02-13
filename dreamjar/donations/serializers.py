from rest_framework import serializers
from django.apps import apps
from campaigns.models import Campaign


class NestedCampaignSerializer(serializers.ModelSerializer):
    child_name = serializers.CharField(source="child.name", read_only=True)
    class Meta:
        model = Campaign
        fields = ['id', 'title', 'description', 'goal', 'child_name']
        
class DonationSerializer(serializers.ModelSerializer):
    campaign = NestedCampaignSerializer(read_only=True)
    class Meta:
        model = apps.get_model('donations.Donation')
        fields = '__all__'
        read_only_fields = ('donor', 'date_donated', 'campaign')

    def validate(self, data):
        request = self.context.get('request')
        anonymous = data.get('anonymous', False)

        # Logged-in users skip validation
        if request.user.is_authenticated:
            return data

        # Non-user donations must provide name/email if not anonymous
        if not request.user.is_authenticated and not anonymous:
            if not data.get('donor_name'):
                raise serializers.ValidationError({"donor_name": "Name is required for non-user donations."})
            if not data.get('donor_email'):
                raise serializers.ValidationError({"donor_email": "Email is required for non-user donations."})

        return data

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Donation amount must be greater than zero.")
        if value > 100000:
            raise serializers.ValidationError("Donation amount exceeds the maximum limit ($100,000).")
        return value

    def get_donor_name(self, obj):
        # Output helper only
        if obj.donor:
            return obj.donor.first_name or obj.donor.username
        if obj.anonymous:
            return "Anonymous"
        return obj.donor_name or "Anonymous"


class PublicDonationSerializer(DonationSerializer):
    class Meta(DonationSerializer.Meta):
        fields = ['id', 'amount', 'date_donated', 'donor_name', 'comment']

    def get_donor_name(self, obj):
        if obj.donor:
            return obj.donor.first_name or obj.donor.username
        if obj.anonymous:
            return "Anonymous"
        return obj.donor_name or "Anonymous"
