import random
import string

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