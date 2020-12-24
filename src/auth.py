"""Module to interface with Auth0 and validate
JWTs before accessing private endpoints. Also controls cross-origin
resource sharing and rate limiting throughout the application.
"""

import json, os
from functools import wraps
from flask import request, current_app
from jose import jwt
import requests
from flask_limiter import Limiter, util
from flask_cors import CORS

from src.exceptions import AuthError, InvalidUsage

limiter = Limiter(key_func=util.get_remote_address, default_limits=["10/second;1000/day"])
cors = CORS()


def get_token_auth_header():
    auth = request.headers.get("Authorization", None)
    if not auth:
        print("Authorization header missing")
        raise AuthError("Authorization header missing")
    
    parts = auth.split()

    if (parts[0].lower() != "bearer") or (len(parts) == 1) or (len(parts) > 2):
        raise AuthError("Authorization token given in the incorrect format")

    token = parts[1]
    return token


def requires_auth(f):
    """Wraps a function view to determine if a given access
    token is valid before accessing a resource. Populates the
    current_user parameter on any view function.
    """
    @wraps(f)
    def decorated(*args, **kwargs):

        if current_app.config['ADMIN_OFF']:
            raise InvalidUsage("Private endpoints have been turned off", status_code=501)

        # Get token from Authorization: Bearer <Token> header
        token = get_token_auth_header()
        # Look through known JSON Web Key Sets:
        known_req = requests.get(f'https://{os.getenv("AUTH0_DOMAIN")}/.well-known/jwks.json')
        jwks = known_req.json()
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = {}
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"]
                }
        
        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    algorithms=["RS256"],
                    audience=os.getenv('AUTH0_API_AUDIENCE'),
                    issuer="https://"+os.getenv('AUTH0_DOMAIN')+"/"
                )
            except jwt.ExpiredSignatureError:
                raise AuthError("Authorization token expired")
            except jwt.JWTClaimsError:
                raise AuthError("Incorrect claims")
            except Exception:
                raise AuthError("Authorization failed")

            return f(*args, **kwargs, current_user=payload)
        raise AuthError("Unable to find required key")
    return decorated