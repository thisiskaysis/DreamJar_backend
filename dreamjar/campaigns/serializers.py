from rest_framework import serializers
from django.apps import apps

class CampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = apps.get_model('campaigns.Campaign')
        fields = '__all__'