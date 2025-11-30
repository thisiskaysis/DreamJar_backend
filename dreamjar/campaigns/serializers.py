from rest_framework import serializers
from django.apps import apps
from donations.serializers import DonationSerializer
from users.models import Child
from campaigns.models import Campaign

class CampaignSerializer(serializers.ModelSerializer):
    """
    For campaign OWNERS view
    Shows full details including child info
    Used when parents view/manage their own children's campaigns
    """
    child = serializers.ReadOnlyField(source='child.id')
    child_name = serializers.ReadOnlyField(source='child.name')
    
    class Meta:
        model = apps.get_model('campaigns.Campaign')
        fields = '__all__'
        read_only_fields = ['child', 'date_created']
    
    def create(self, validated_data):
        # Connect the campaign to the child from context
        child_id = self.context.get('child_id')
        child = Child.objects.get(id=child_id)
        campaign = Campaign.objects.create(child=child, **validated_data)
        return campaign
    
    def validate_goal(self, value):
        if value <= 0:
            raise serializers.ValidationError("DreamJar goal must be greater than zero.")
        if value > 100000:
            raise serializers.ValidationError("DreamJar goal exceed maximum amount ($100,000)")

class PublicCampaignSerializer(serializers.ModelSerializer):
    """
    For PUBLIC viewing
    Hides sensitive information
    Shows ONLY child's first name
    """
    child_name = serializers.SerializerMethodField()
    total_raised = serializers.SerializerMethodField()
    donor_count = serializers.SerializerMethodField()
    percentage_funded = serializers.SerializerMethodField()

    class Meta:
        model = apps.get_model('campaigns.Campaign')
        fields = ['id', 'child_name', 'title', 'description', 'goal', 'image', 'is_open', 'date_created', 'total_raised', 'donor_count', 'percentage_funded']
    
    def get_child_name(self, obj):
        return obj.child.name
    
    def get_total_raised(self, obj):
        return sum(donation.amount for donation in obj.donations.all())
    
    def get_donor_count(self, obj):
        return obj.donations.count()
    
    def get_percentage_funded(self, obj):
        total = self.get_total_raised(obj)
        return round((total / obj.goal * 100), 1) if obj.goal > 0 else 0

class CampaignDetailSerializer(CampaignSerializer):
    """
    For campaign OWNER
    Includes full donation list
    Inherits from CampaignSerializer and adds donations
    """

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
    
    def get_total_raised(self, obj):
        return sum(donation.amount for donation in obj.donations.all())