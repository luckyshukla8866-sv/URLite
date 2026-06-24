from django.urls import path
from .views import ShortenURLView, RedirectURLView, AnalyticsView

urlpatterns = [
    # Our API endpoints
    path('api/shorten/', ShortenURLView.as_view(), name='shorten_url'),
    path('api/analytics/<str:short_code>/', AnalyticsView.as_view(), name='url_analytics'),
    
    # The actual redirect route (Notice this is at the root level, like short.ly/aB12Cd)
    path('<str:short_code>/', RedirectURLView.as_view(), name='redirect_url'),
]