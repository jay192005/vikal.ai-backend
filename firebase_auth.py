"""
Firebase Authentication Module
Handles Firebase Admin SDK initialization and token verification
"""

import os
import json
import firebase_admin
from firebase_admin import credentials, auth
from functools import wraps
from flask import request, jsonify, g
import traceback

# Global Firebase app instance
firebase_app = None

def initialize_firebase_auth():
    """
    Initialize Firebase Admin SDK using credentials file or environment variable.
    
    Priority:
    1. FIREBASE_CREDENTIALS environment variable (for production/Render)
    2. firebase_credentials.json file (for local development)
    
    Returns:
        Firebase app instance if successful, None otherwise
    """
    global firebase_app
    
    try:
        # Check if already initialized
        if firebase_app is not None:
            print("✅ Firebase already initialized")
            return firebase_app
        
        # Try to load from environment variable first (for production)
        firebase_creds = os.environ.get('FIREBASE_CREDENTIALS')
        
        if firebase_creds:
            print("🔧 Loading Firebase credentials from environment variable...")
            try:
                # Parse JSON from environment variable
                cred_dict = json.loads(firebase_creds)
                cred = credentials.Certificate(cred_dict)
                print("✅ Firebase credentials loaded from environment")
            except json.JSONDecodeError as e:
                print(f"⚠️ Invalid JSON in FIREBASE_CREDENTIALS: {e}")
                return None
        else:
            # Fallback to file (for local development)
            print("🔧 Loading Firebase credentials from file...")
            cred = credentials.Certificate('firebase_credentials.json')
            print("✅ Firebase credentials loaded from file")
        
        # Initialize Firebase Admin SDK
        firebase_app = firebase_admin.initialize_app(cred)
        
        print("✅ Firebase Authentication initialized successfully")
        return firebase_app
        
    except FileNotFoundError:
        print("⚠️ Firebase credentials file not found. Authentication features disabled.")
        print("💡 For production, set FIREBASE_CREDENTIALS environment variable")
        return None
    except ValueError as e:
        print(f"⚠️ Invalid Firebase credentials: {e}")
        return None
    except Exception as e:
        print(f"⚠️ Firebase initialization failed: {e}")
        traceback.print_exc()
        return None


def verify_id_token(id_token):
    """
    Verify Firebase ID token and extract claims.
    
    Args:
        id_token: JWT token from Firebase Authentication
        
    Returns:
        Dictionary containing user claims (uid, email, etc.) if valid
        None if token is invalid or expired
    """
    try:
        # Verify the token
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except auth.InvalidIdTokenError:
        print("⚠️ Invalid ID token")
        return None
    except auth.ExpiredIdTokenError:
        print("⚠️ Expired ID token")
        return None
    except Exception as e:
        print(f"⚠️ Token verification error: {e}")
        return None


def require_auth(f):
    """
    Decorator to protect Flask routes with Firebase authentication.
    
    Extracts and verifies ID token from Authorization header.
    Attaches user_id to Flask g object for use in route handlers.
    
    Returns 401 if token is missing, invalid, or expired.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if Firebase is initialized
        if firebase_app is None:
            return jsonify({
                'error': 'Authentication service unavailable',
                'message': 'Firebase authentication is not configured'
            }), 503
        
        # Extract Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Authorization header missing'
            }), 401
        
        # Parse Bearer token
        try:
            scheme, token = auth_header.split(' ')
            if scheme.lower() != 'bearer':
                return jsonify({
                    'error': 'Unauthorized',
                    'message': 'Invalid authorization scheme. Use Bearer token'
                }), 401
        except ValueError:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid authorization header format'
            }), 401
        
        # Verify token
        decoded_token = verify_id_token(token)
        
        if decoded_token is None:
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid or expired token'
            }), 401
        
        # Attach user_id to request context
        g.user_id = decoded_token.get('uid')
        g.user_email = decoded_token.get('email')
        
        # Call the original function
        return f(*args, **kwargs)
    
    return decorated_function
