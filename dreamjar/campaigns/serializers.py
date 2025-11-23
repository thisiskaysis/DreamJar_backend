from rest_framework import serializers
from django.apps import apps
from donations.serializers import DonationSerializer
from users.models import Child
from campaigns.models import Campaign

class CampaignSerializer(serializers.ModelSerializer):
    # I forgot why I might need these
    child = serializers.ReadOnlyField(source='child.id')
    child_name = serializers.ReadOnlyField(source='child.name')
    
    class Meta:
        model = apps.get_model('campaigns.Campaign')
        fields = '__all__'
        read_only_fields = ['child', 'date_created']
    
    def create(self, validated_data):
        # Connect the campaign to the child from context
        child_id = self.context['child_id']
        child = Child.objects.get(id=child_id)
        campaign = Campaign.objects.create(child=child, **validated_data)
        return campaign

class CampaignDetailSerializer(CampaignSerializer):
    
    # Include all donations for this campaign & total amount
    # Do I put these here or views?
    donations = DonationSerializer(many=True, read_only=True)
    total_donated = serializers.SerializerMethodField()
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.goal = validated_data.get('goal', instance.goal)
        instance.image = validated_data.get('image', instance.image)
        instance.is_open = validated_data.get('is_open', instance.is_open)
        instance.save()
        return instance
    
    def get_total_donated(self, obj):
        return sum(donation.amount for donation in obj.donations.all())