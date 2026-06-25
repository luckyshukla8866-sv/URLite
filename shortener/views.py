from django.shortcuts import redirect, get_object_or_404
from django.db.models import F,Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from .models import ShortenedURL
from .serializers import URLSerializer
from .utils import generate_short_code
from .utils import generate_short_code, validate_url
class ShortenURLView(APIView):
    """
    POST /api/shorten/
    Accepts a long URL, generates a short code, and saves it.
    """
    def post(self, request):
        try:
            original_url = request.data.get('original_url')
            custom_alias = request.data.get('custom_alias')
            expires_at = request.data.get('expires_at')

            # 2. Basic Validation: Make sure they actually sent a URL
            if not original_url:
                return Response({
                    "status":"failed",
                    "message": "original_url is required."
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # 3. Deep Validation: Check if the URL is alive using our util function
            is_valid, error_msg = validate_url(original_url)
            if not is_valid:
                return Response({
                    "status":"failed",
                    "message": [error_msg],
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # 4. Check if the custom alias is already taken in the database
            if custom_alias:
                if ShortenedURL.objects.filter(custom_alias=custom_alias).exists():
                    return Response({
                        "status":"failed",
                        "message": "This custom alias is already taken."
                        }, status=status.HTTP_400_BAD_REQUEST)
            
            # 5. Save the data manually to the database
            code = generate_short_code()
            url_obj = ShortenedURL.objects.create(
                original_url=original_url,
                short_code=code,
                custom_alias=custom_alias,
                expires_at=expires_at
            )

            # 6. Manually build the final short_url string
            final_code = url_obj.custom_alias if url_obj.custom_alias else url_obj.short_code
            short_url = request.build_absolute_uri(f"/{final_code}/")

            # 7. Manually build the JSON dictionary to send back to the user
            response_data = {
                "id": url_obj.id,
                "original_url": url_obj.original_url,
                "short_code": url_obj.short_code,
                "custom_alias": url_obj.custom_alias,
                "expires_at": url_obj.expires_at,
                "short_url": short_url,
                "click_count": url_obj.click_count,
                "created_at": url_obj.created_at
            }

            return Response(response_data, status=status.HTTP_201_CREATED)
        
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
    def get(self, request,short_code):
        try:    
            # Look up the code in the DB. If it doesn't exist, return a 404 error automatically.
            url_obj = get_object_or_404(ShortenedURL, Q(short_code=short_code) | Q(custom_alias=short_code))
           
            # Does an expiration date exist? 
            # Is right now greater than the expiration date?
            if url_obj.expires_at and timezone.now() > url_obj.expires_at:
                return Response({
                    "status":"failed",
                    "message": "Sorry! This link has expired and is no longer active."
                    },status=status.HTTP_410_GONE)
            
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
    def post(self, request):
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

            final_code = url_obj.custom_alias if url_obj.custom_alias else url_obj.short_code

            response_data = {
                "id": url_obj.id,
                "original_url": url_obj.original_url,
                "short_code": url_obj.short_code,
                "custom_alias": url_obj.custom_alias,
                "expires_at": url_obj.expires_at,
                "short_url": request.build_absolute_uri(f"/{final_code}/"),
                "click_count": url_obj.click_count,
                "created_at": url_obj.created_at
            }
            
            return Response({
                "status":"success",
                "message":"Analyzed the link successsfully", 
                "data":response_data
                },status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                "status":"error",
                "message":str(e)
            })