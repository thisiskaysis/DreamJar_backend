from django.db import models
from users.models import Child

# Create your models here.
class Campaign(models.Model):
    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='owned_campaigns'
    )
    title = models.CharField(max_length=200)
    description = models.TextField()
    goal = models.IntegerField()
    image = models.URLField()
    is_open = models.BooleanField()
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    