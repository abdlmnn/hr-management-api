"""
Utility endpoints URLs.
Refer to BACKGROUND_REMOVAL_DOCUMENTATION.md for endpoint details.
"""

from django.urls import path

app_name = 'utils'

# Lazy import prevents startup failures if dependencies are missing
try:
    from .views import RemoveBackgroundView
    urlpatterns = [
        path('remove-background/', RemoveBackgroundView.as_view(), name='remove-background'),
    ]
except ImportError:
    urlpatterns = []

