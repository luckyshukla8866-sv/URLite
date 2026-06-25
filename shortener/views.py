from django.shortcuts import redirect, get_object_or_404
from django.db.models import F,Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import ShortenedURL
from .serializers import URLSerializer
from .utils import generate_short_code

class ShortenURLView(APIView):
    """
    POST /api/shorten/
    Accepts a long URL, generates a short code, and saves it.
    """
    def post(self, request):
        try:
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
        
        except Exception as e:
            return Response({
                "status":"error",
                "message":str(e)
            })


class RedirectURLView(APIView):
    """
    GET /<short_code>/
    Finds the original URL, increments the click count, and redirects.
    """
    def get(self, request):
        try:    
            short_code=request.data.get("short_code")

            # Look up the code in the DB. If it doesn't exist, return a 404 error automatically.
            url_obj = get_object_or_404(ShortenedURL, Q(short_code=short_code) | Q(custom_alias=short_code))
           
            # Does an expiration date exist? 
            # Is right now greater than the expiration date?
            if url_obj.expires_at and timezone.now() > url_obj.expires_at:
                return Response(
                    {"error": "Sorry! This link has expired and is no longer active."}, 
                    status=status.HTTP_410_GONE
                )
            
            # Increment the click count safely using Django's F() expression
            # F() expressions tell the database to add 1 directly, preventing race conditions
            url_obj.click_count = F('click_count') + 1
            url_obj.save()
                    
            # 3. Perform the HTTP 302 Temporary Redirect to the long URL
            return redirect(url_obj.original_url)
        
        except Exception as e:
            return Response({
                "status":"error",
                "message":str(e)
            })

class AnalyticsView(APIView):
    """
    GET /api/analytics/<short_code>/
    Returns the stats for a specific short link.
    """
    def get(self, request):
        try:
            short_code=request.data.get("short_code")
            url_obj = get_object_or_404(ShortenedURL, Q(short_code=short_code) | Q(custom_alias=short_code))
            
            if url_obj.expires_at and timezone.now() > url_obj.expires_at:
                return Response(
                    {"error": "This link has expired. Analytics are closed."}, 
                    status=status.HTTP_410_GONE
                )
            # We need to refresh from the DB because we used F() expressions for click_count
            url_obj.refresh_from_db() 
            
            serializer = URLSerializer(url_obj, context={'request': request})
    
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                "status":"error",
                "message":str(e)
            })