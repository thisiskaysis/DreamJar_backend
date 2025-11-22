from rest_framework import serializers
from django.apps import apps

class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        Donation = apps.get_model('donations.Donation')
        fields = '__all__'