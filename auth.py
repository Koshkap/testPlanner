from functools import wraps
from flask import session, redirect, url_for
from supabase import create_client, Client
import os
from urllib.parse import urlparse
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    logger.error("Missing Supabase credentials. Both SUPABASE_URL and SUPABASE_KEY must be set.")
    raise ValueError("Missing Supabase credentials")

try:
    # Log URL structure for debugging (without exposing the actual URL)
    parsed_url = urlparse(supabase_url)
    logger.debug(f"URL structure - scheme: {bool(parsed_url.scheme)}, netloc: {bool(parsed_url.netloc)}")

    if not all([parsed_url.scheme, parsed_url.netloc]):
        raise ValueError("Invalid Supabase URL format. Must be a complete URL with scheme and host.")

    # Initialize the client
    supabase: Client = create_client(supabase_url, supabase_key)
    logger.info("Supabase client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
    raise

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
