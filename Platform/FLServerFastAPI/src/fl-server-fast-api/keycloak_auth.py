# auth.py
import logging
import os

import yaml
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt, JWTError, ExpiredSignatureError
from keycloak import KeycloakOpenID, KeycloakAdmin
from keycloak.exceptions import KeycloakAuthenticationError
import httpx, time

from mongo import get_db

logger = logging.getLogger("uvicorn.error")

# ----------------------------
# Configuration
# ----------------------------
config_path = os.path.dirname(__file__) + "/config.yml"
with open(config_path, "r") as file:
    config = yaml.safe_load(file)
    KEYCLOAK_SERVER_URL = config["keycloak"]["url"]
    KEYCLOAK_REALM = config["keycloak"]["realm"]
    KEYCLOAK_CLIENT_ID = config["keycloak"]["api_client_id"]
    KEYCLOAK_CLIENT_SECRET = config["keycloak"]["api_client_secret"]
    KEYCLOAK_ALGO = "RS256"

# ----------------------------
# Keycloak client initialization
# ----------------------------
keycloak_openid = KeycloakOpenID(
    server_url=KEYCLOAK_SERVER_URL,
    realm_name=KEYCLOAK_REALM,
    client_id=KEYCLOAK_CLIENT_ID,
    client_secret_key=KEYCLOAK_CLIENT_SECRET,
)

# ----------------------------
# Token / JWKS cache
# ----------------------------
_jwks_cache = None
_jwks_expiry = 0

security = HTTPBearer()

async def get_jwks():
    global _jwks_cache, _jwks_expiry
    if _jwks_cache and time.time() < _jwks_expiry:
        return _jwks_cache

    url = f"{KEYCLOAK_SERVER_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        _jwks_cache = resp.json()
        _jwks_expiry = time.time() + 3600  # cache 1h
        return _jwks_cache


# ----------------------------
# JWT Validation
# ----------------------------
async def verify_token(token: str):
    """Verify and decode JWT using Keycloak's JWKS."""
    jwks = await get_jwks()
    header = jwt.get_unverified_header(token)
    jwk = next((k for k in jwks["keys"] if k["kid"] == header["kid"]), None)
    if not jwk:
        raise HTTPException(status_code=401, detail="Invalid token key id")

    try:
        payload = jwt.decode(
            token,
            key=jwk,
            algorithms=[KEYCLOAK_ALGO],
            audience=KEYCLOAK_CLIENT_ID,
            options={"verify_exp": True},
        )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")


# ----------------------------
# Token Refresh
# ----------------------------
async def refresh_access_token(refresh_token: str):
    """Refresh expired access token using the refresh token."""
    try:
        new_token = keycloak_openid.refresh_token(refresh_token)
        return new_token  # contains 'access_token' and 'refresh_token'
    except KeycloakAuthenticationError as e:
        raise HTTPException(status_code=401, detail="Invalid refresh token")


# ----------------------------
# User Info (optional)
# ----------------------------
async def get_userinfo(access_token: str):
    """Fetch user profile info from Keycloak's /userinfo endpoint."""
    try:
        userinfo = keycloak_openid.userinfo(access_token)
        return userinfo
    except KeycloakAuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid access token")


# ----------------------------
# Dependencies for FastAPI
# ----------------------------

async def get_current_user(credentials=Depends(security)):
    token = credentials.credentials
    return await verify_token(token)


def require_role(role_name: str, in_client: str | None = None):
    """Dependency ensuring a specific realm/client role."""
    async def dependency(user=Depends(get_current_user)):
        roles = user.get("realm_access", {}).get("roles", [])
        if in_client:
            client_roles = user.get("resource_access", {}).get(in_client, {}).get("roles", [])
            roles.extend(client_roles)
        if role_name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing required role: {role_name}",
            )
        return user

    return dependency

def get_keycloak_admin():
    if not require_role("admin"):
        raise HTTPException(status_code=403, detail="Forbidden")

    return KeycloakAdmin(
        server_url=f"{KEYCLOAK_SERVER_URL}/",
        realm_name=KEYCLOAK_REALM,
        client_id=KEYCLOAK_CLIENT_ID,
        client_secret_key=KEYCLOAK_CLIENT_SECRET,
        verify=True,
    )

def require_user_in_group(group_id: str, admin_allowed=False):
    def dependency(token: dict = Depends(get_current_user)):
        if not (admin_allowed and require_role("admin")):
            if not keycloak_user_in_group(group_id, token["sub"]):
                raise HTTPException(status_code=403, detail="User not in group")
        return token

    return dependency


def keycloak_user_in_group(group_id, user_id, db = get_db()):
    group = db.groups.find_one({"_id": group_id})
    users = db.users.find({"_governance_id": {"$in": group["members"]}})
    if any(user_id == user["_governance_id"] for user in users):
        return True
    return False
