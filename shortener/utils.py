import random
import string
import requests
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

def generate_short_code():
    # Define our character set: abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789
    characters = string.ascii_letters + string.digits
    
    # We import the model inside the function to avoid circular import issues in Django
    from .models import ShortenedURL
   
    while True:
        # 1. Pick 6 random characters and join them into a string
        code = ''.join(random.choices(characters, k=6))
        
        # 2. Check if this code already exists in our database
        if not ShortenedURL.objects.filter(short_code=code).exists():
            # If it does not exist, our code is safe and unique! Return it.
            return code
        
        # If it does exist, the loop naturally continues to generate a new one.


def validate_url(url):
    """
    Manually checks if the URL syntax is correct and if the website is alive.
    Returns a tuple: (is_valid_boolean, error_message)
    """
    # 1. Check basic syntax (e.g. does it start with http:// or https://)
    validator = URLValidator()
    try:
        validator(url)
    except ValidationError:
        return False, "Invalid URL format."
        
    # 2. Check if the website is actually alive on the internet
    try:
        response = requests.head(url, timeout=3, allow_redirects=True)
        response.raise_for_status()
    except requests.RequestException:
        return False, "This URL does not exist or is unreachable."
        
    return True, "URL is valid."