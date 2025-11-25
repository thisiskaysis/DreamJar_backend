from rest_framework import serializers
from django.apps import apps

class DonationSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = apps.get_model('donations.Donation')
        fields = '__all__'

class DonationDetailSerializer(DonationSerializer):
    
    def update(self, instance, validated_data):
        instance.amount = validated_data.get('amount', instance.amount)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.anonymous = validated_data.get('anonymous', instance.anonymous)
        instance.campaign = validated_data.get('campaign', instance.campaign)
        instance.donor = validated_data.get('donor', instance.donor)
        instance.save()
        return instance