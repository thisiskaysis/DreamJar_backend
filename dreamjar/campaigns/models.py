from django.db import models
from users.models import Child
from django.utils import timezone

# Create your models here.
class Campaign(models.Model):
    """Links campaign to a child and contains campaign details"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal = models.IntegerField()
    image = models.URLField(null=True, blank=True)
    is_open = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)
    category = models.CharField(max_length=50,
        choices=[
        ('sports', 'Sports'),
        ('education', 'Education'),
        ('hobbies', 'Hobbies'),
        ('health', 'Health'),
        ('dreams', 'Dreams'),
        ])
    
    # Link campaign to a specific child
    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='owned_campaigns'
    )

    # Optional deadline
    has_deadline = models.BooleanField(default=False)
    deadline = models.DateTimeField(null=True, blank=True)

    # ---- BUSINESS LOGIC PROPERTIES ----

    @property
    def total_raised(self):
        """Return the total amount raised for this campaign"""
        donations = self.donations.all()
        total = sum(donation.amount for donation in donations)
        return total
    
    @property
    def donation_count(self):
        """Return number of donations"""
        return self.donations.count()
    
    @property
    def percentage_raised(self):
        """Return percentage of goal raised"""
        total = self.total_raised
        if self.goal == 0:
            return 0
        return round((total / self.goal * 100), 1)
    
    @property
    def is_expired(self):
        """Whether the campaign has ended"""
        if self.has_deadline and self.deadline:
            return timezone.now() > self.deadline
        return False
    
    @property
    def seconds_remaining(self):
        """Return seconds remaining until deadline, or None if no deadline"""
        if self.has_deadline and self.deadline:
            delta = self.deadline - timezone.now()
            return max(int(delta.total_seconds()), 0)
        return None

    def __str__(self):
        return f"{self.title} (Child: {self.child.name})"
    