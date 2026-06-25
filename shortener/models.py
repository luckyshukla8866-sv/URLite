from django.db import models

# Create your models here.
from django.db import models

class ShortenedURL(models.Model):
    # The original long URL
    original_url = models.URLField(max_length=2048)
    
    # The unique 6-character code. db_index=True makes database searches incredibly fast!
    short_code = models.CharField(max_length=10, unique=True, db_index=True)

    custom_alias = models.CharField(max_length=15, null=True, blank=True, unique=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    # Analytics tracking
    click_count = models.IntegerField(default=0)
    
    # Automatically set the date and time when the link is created
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # This controls how the object is displayed in the Django admin panel
        return f"{self.short_code} -> {self.original_url[:30]}..."