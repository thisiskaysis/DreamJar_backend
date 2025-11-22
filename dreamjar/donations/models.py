from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.
class Donation(models.Model):
    amount = models.IntegerField()
    comment = models.CharField(max_length=200, blank=True)
    anonymous = models.BooleanField()
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