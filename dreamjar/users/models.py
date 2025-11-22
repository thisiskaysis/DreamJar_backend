from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
class Parent(AbstractUser):
    
    def __str__(self):
        return self.username
    
class Child(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.URLField(max_length=200, null=True, blank=True)
    
    def __str__(self):
        return self.name