"""
Rate limiting configuration for the API.
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Initialize rate limiter
# Default: 100 requests per hour per IP
limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"])
