from rest_framework import serializers
from .models import Parent, Child

class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }
    def create(self, validated_data):
        return Parent.objects.create_user(**validated_data)
    
class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = '__all__'
        read_only_fields = ['parent'] #Parent is assigned automatically, not via user input
    
    def create(self, validated_data):
        # Set the parent to the currently authenticated user
        parent = self.context['request'].user
        return Child.objects.create(parent=parent, **validated_data)