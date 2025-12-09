from django.db import models
from campaigns.models import Campaign
from django.contrib.auth import get_user_model

# Create your models here.
class Donation(models.Model):
    amount = models.IntegerField()
    comment = models.CharField(max_length=200, blank=True)
    anonymous = models.BooleanField(default=False) #when True, donor's name won't be displayed publicly
    date_donated = models.DateTimeField(auto_now_add=True)
    stripe_payment_intent_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    stripe_transfer_id = models.CharField(max_length=255, blank=True, null=True)
    transferred_to_creator = models.BooleanField(default=False)
    status = models.CharField(max_length=50, default='pending',
        choices=[
        ('pending', 'Pending'),
        ('succeeded', 'Succeeded'),
        ('failed', 'Failed')
        ])

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

    class Meta:
        ordering = ['-date_donated']

    def __str__(self):
        donor_name = self.donor.username if self.donor else self.donor_name or "Anonymous"
        return f"{donor_name} has donated ${self.amount} - {self.get_status_display()}"
    
    @property
    def display_donor_name(self):
        if self.anonymous:
            return "Anonymous"
        if self.donor:
            return self.donor.get_full_name() or self.donor.username
        return self.donor_name or "Anonymous"