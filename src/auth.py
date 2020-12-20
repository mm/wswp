"""Module to interface with Auth0 and validate
JWTs before accessing private endpoints.
"""

import json, os
from functools import wraps
from flask import request

from jose import jwt
import requests


class AuthError(Exception):
    def __init__(self, error, status_code=401):
        self.error = error
        self.status_code = status_code


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
    token is valid before accessing a resource.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
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


def requires_scope(required_scope):
    """Determines if the required scope is present in the Access Token passed.
    Note: This doesn't perform validation and is designed to be run after the
    token was validated.
    """

    token = get_token_auth_header()
    unverified_claims = jwt.get_unverified_claims(token)
    if unverified_claims.get("scope"):
            token_scopes = unverified_claims["scope"].split()
            for token_scope in token_scopes:
                if token_scope == required_scope:
                    return True
    return False