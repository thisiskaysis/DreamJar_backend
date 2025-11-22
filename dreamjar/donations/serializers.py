from rest_framework import serializers
from django.apps import apps

class DonationSerializer(serializers.ModelSerializer):
    donor = serializers.ReadOnlyField(source='donor.id') 
    class Meta:
        model = apps.get_model('donations.Donation')
        fields = '__all__'

class DonationDetailSerializer(DonationSerializer):
    
    def update(self, instance, validated_data):
        instance.amount = validated_data.get('amount', instance.amount)
        instance.comment = validated_data.get('comment', instance.comment)
        instance.anonymous = validated_data.get('anonymous', instance.anonymous)
        instance.fundraiser = validated_data.get('fundraiser', instance.fundraiser)
        instance.supporter = validated_data.get('supporter', instance.supporter)
        instance.save()
        return instance