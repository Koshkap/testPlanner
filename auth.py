import os
import logging
from supabase import create_client, Client
from flask import session
from flask_login import UserMixin

logger = logging.getLogger(__name__)

class User(UserMixin):
    def __init__(self, user_data):
        self.id = user_data.get('id')
        self.email = user_data.get('email')

class SupabaseAuth:
    def __init__(self):
        url: str = os.environ.get("SUPABASE_URL")
        key: str = os.environ.get("SUPABASE_KEY")

        if not url or not key:
            logger.error("Missing required environment variables")
            raise ValueError("Missing required environment variables: SUPABASE_URL or SUPABASE_KEY")

        # Validate URL format
        if not url.startswith(('http://', 'https://')):
            logger.error(f"Invalid Supabase URL format: {url[:10]}...")
            raise ValueError("Supabase URL must start with http:// or https://")

        # Validate key format (Supabase keys typically start with 'eyJ')
        if not key.startswith('eyJ'):
            logger.error("Invalid Supabase key format")
            raise ValueError("Invalid Supabase key format. Make sure you're using the project's anon/public key")

        logger.info("Initializing Supabase client")
        try:
            self.supabase: Client = create_client(url, key)
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {str(e)}")
            raise Exception(f"Failed to initialize Supabase client: {str(e)}")

    def sign_up(self, email: str, password: str) -> dict:
        try:
            logger.info(f"Attempting to sign up user: {email}")
            response = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            logger.info(f"Sign up response received: {type(response)}")

            if hasattr(response, 'error') and response.error:
                logger.error(f"Supabase signup error: {response.error}")
                return {"success": False, "error": str(response.error)}

            if not response.user:
                logger.error("Failed to create user: No user data returned")
                return {"success": False, "error": "Failed to create user"}

            logger.info("User signed up successfully")
            return {"success": True, "user": response.user}
        except Exception as e:
            logger.error(f"Sign up error: {str(e)}")
            return {"success": False, "error": str(e)}

    def sign_in(self, email: str, password: str) -> dict:
        try:
            logger.info(f"Attempting to sign in user: {email}")
            response = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            logger.info(f"Sign in response received: {type(response)}")

            if hasattr(response, 'error') and response.error:
                logger.error(f"Supabase login error: {response.error}")
                return {"success": False, "error": str(response.error)}

            if not response.user:
                logger.error("Invalid credentials: No user data returned")
                return {"success": False, "error": "Invalid credentials"}

            user_data = {
                'id': response.user.id,
                'email': response.user.email,
            }

            logger.info("User signed in successfully")
            return {
                "success": True, 
                "user": User(user_data),
                "session": response.session
            }
        except Exception as e:
            logger.error(f"Sign in error: {str(e)}")
            return {"success": False, "error": str(e)}

    def sign_out(self) -> dict:
        try:
            logger.info("Attempting to sign out user")
            self.supabase.auth.sign_out()
            logger.info("User signed out successfully")
            return {"success": True}
        except Exception as e:
            logger.error(f"Sign out error: {str(e)}")
            return {"success": False, "error": str(e)}

    def get_user(self) -> dict:
        try:
            user = self.supabase.auth.get_user()
            return {"success": True, "user": user}
        except Exception:
            return {"success": False, "user": None}