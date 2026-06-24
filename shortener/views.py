from django.shortcuts import redirect, get_object_or_404
from django.db.models import F
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import ShortenedURL
from .serializers import URLSerializer
from .utils import generate_short_code

class ShortenURLView(APIView):
    """
    POST /api/shorten/
    Accepts a long URL, generates a short code, and saves it.
    """
    def post(self, request):
        # 1. Pass the incoming JSON data to our serializer
        serializer = URLSerializer(data=request.data, context={'request': request})
        
        # 2. Check if the data is valid (e.g., is it a real URL?)
        if serializer.is_valid():
            # 3. Generate our unique 6-character code
            code = generate_short_code()
            
            # 4. Save the new object to the database
            serializer.save(short_code=code)
            
            # 5. Return the created data and a 201 Created status
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        # If the data was invalid, return a 400 Bad Request error
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RedirectURLView(APIView):
    """
    GET /<short_code>/
    Finds the original URL, increments the click count, and redirects.
    """
    def get(self, request, short_code):
        # 1. Look up the code in the DB. If it doesn't exist, return a 404 error automatically.
        url_obj = get_object_or_404(ShortenedURL, short_code=short_code)
        
        # 2. Increment the click count safely using Django's F() expression
        # F() expressions tell the database to add 1 directly, preventing race conditions
        url_obj.click_count = F('click_count') + 1
        url_obj.save()
        
        # 3. Perform the HTTP 302 Temporary Redirect to the long URL
        return redirect(url_obj.original_url)


class AnalyticsView(APIView):
    """
    GET /api/analytics/<short_code>/
    Returns the stats for a specific short link.
    """
    def get(self, request, short_code):
        url_obj = get_object_or_404(ShortenedURL, short_code=short_code)
        
        # We need to refresh from the DB because we used F() expressions for click_count
        url_obj.refresh_from_db() 
        
        serializer = URLSerializer(url_obj, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)