from django.db import models
from campaigns.models import Campaign
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone

# Create your models here.
class Donation(models.Model):
    amount = models.IntegerField()
    comment = models.CharField(max_length=200, blank=True)
    anonymous = models.BooleanField()
    date_donated = models.DateTimeField(auto_now_add=True)
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        on_delete=models.CASCADE,
        related_name='donations'
    )
    donor = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='donations'
    )

    def __str__(self):
        return f"Donation of {self.amount} to {self.campaign.title} by {self.donor.username}"