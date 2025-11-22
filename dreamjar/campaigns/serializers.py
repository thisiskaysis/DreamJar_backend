from rest_framework import serializers
from django.apps import apps
from donations.serializers import DonationSerializer
from users.models import Child
from campaigns.models import Campaign

class CampaignSerializer(serializers.ModelSerializer):
    child = serializers.ReadOnlyField(source='child.id')
    class Meta:
        model = apps.get_model('campaigns.Campaign')
        fields = '__all__'
        read_only_fields = ['child']
    
    def create(self, validated_data):
        #Pass child_id through the view context
        child_id = self.context['child_id']
        child = Child.objects.get(id=child_id)
        campaign = Campaign.objects.create(child=child, **validated_data)
        return campaign

class CampaignDetailSerializer(CampaignSerializer):
    donations = DonationSerializer(many=True, read_only=True)
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.description = validated_data.get('description', instance.description)
        instance.goal = validated_data.get('goal', instance.goal)
        instance.image = validated_data.get('image', instance.image)
        instance.is_open = validated_data.get('is_open', instance.is_open)
        instance.date_created = validated_data.get('date_created', instance.date_created)
        instance.child = validated_data.get('child', instance.child)
        instance.save()
        return instance