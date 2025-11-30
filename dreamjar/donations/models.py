from django.db import models
from campaigns.models import Campaign
from django.contrib.auth import get_user_model

# Create your models here.
class Donation(models.Model):
    amount = models.IntegerField()
    comment = models.CharField(max_length=200, blank=True)
    anonymous = models.BooleanField(default=False) #when True, donor's name won't be displayed publicly
    date_donated = models.DateTimeField(auto_now_add=True)

    #Link donation to a specific campaign and donor
    campaign = models.ForeignKey(
        'campaigns.Campaign',
        on_delete=models.CASCADE,
        related_name='donations'
    )

    donor = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='donations',
        null=True, blank=True
    ) # Allow null for anonymous donations

    # Optional donor details for anonymous donations
    donor_name = models.CharField(max_length=100, blank=True)
    donor_email = models.EmailField(blank=True)

    def __str__(self):
        return f"{self.donor.name} has donated {self.amount} to {self.campaign.child.name}"