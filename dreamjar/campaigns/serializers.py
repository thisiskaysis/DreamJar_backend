from rest_framework import serializers
from django.apps import apps
from donations.serializers import DonationSerializer

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model('campaigns.Campaign')
        fields = '__all__'

class CampaignDetailSerializer(CampaignSerializer):
    donations = DonationSerializer(many=True, read_only=True)

    # class Meta(CampaignSerializer.Meta):
    #     fields = CampaignSerializer.Meta.fields + ['donations']
    # ^^^ Do I need this?