from rest_framework import serializers
from .models import ShortenedURL

class URLSerializer(serializers.ModelSerializer):
    # We add an explicit field for the final computed short URL string
    short_url = serializers.SerializerMethodField()

    class Meta:
        model = ShortenedURL
        # These are the fields sent to or received by the API client
        fields = ['id', 'original_url', 'short_code', 'custom_alias', 'expires_at','short_url', 'click_count', 'created_at']
        # Read-only fields cannot be manipulated or injected by the client request payload
        read_only_fields = ['short_code', 'click_count', 'created_at']

    def get_short_url(self, obj):
        # Access the current HTTP request context to build a complete absolute URL path
        request = self.context.get('request')

        if obj.custom_alias:
            final_code = obj.custom_alias
        else:
            final_code = obj.short_code

        if request is not None:
            return request.build_absolute_uri(f"/{final_code}/")
        return f"http://localhost:8000/{final_code}/"