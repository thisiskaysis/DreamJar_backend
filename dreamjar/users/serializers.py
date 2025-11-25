from rest_framework import serializers
from datetime import date
from .models import Parent, Child

class ParentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parent
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8}
        } #added min length for password field

    def create(self, validated_data):
        return Parent.objects.create_user(**validated_data)
    
    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Username must be at least 3 characters long.")
        return value
    
class ChildSerializer(serializers.ModelSerializer):
    class Meta:
        model = Child
        fields = '__all__'
        read_only_fields = ['parent'] #Parent is assigned automatically, not via user input
    
    def create(self, validated_data):
        # Set the parent to the currently authenticated user
        parent = self.context['request'].user
        return Child.objects.create(parent=parent, **validated_data)
    
    def validate_name(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Child name must be at least 2 characters long.")
        return value
    
    def validate_date_of_birth(self, value):
        age = date.today().year - value.year
        
        if value > date.today():
            raise serializers.ValidationError("Date of birth cannot be in the future.")
        
        if age > 16:
            raise serializers.ValidationError("Child must be under 16 years.")
        return value