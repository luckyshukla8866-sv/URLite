from django.contrib import admin
from .models import ShortenedURL

# Register your models here.

@admin.register(ShortenedURL)
class ShortenedURLAdmin(admin.ModelAdmin):
    # This configures which columns show up in the admin table
    list_display = ('short_code', 'original_url', 'click_count', 'created_at')
    # This adds a search bar so you can find URLs easily
    search_fields = ('short_code', 'original_url')