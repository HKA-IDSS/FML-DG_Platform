# auth.py
import os

import yaml
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from jose import jwt, JWTError, ExpiredSignatureError
from keycloak import KeycloakOpenID, KeycloakAdmin
from keycloak.exceptions import KeycloakAuthenticationError
import httpx, time

from federatedmlrest.api.DBConnection import get_db

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

#
# config_path = os.path.dirname(__file__) + "/config.yml"
# with open(config_path, "r") as file:
#     config = yaml.safe_load(file)
#     keycloak_url = config["keycloak"]["url"]
#     keycloak_introspect_url = config["keycloak"]["url"]
#     realm = config["keycloak"]["realm"]
#     api_client_id = config["keycloak"]["api_client_id"]
#     api_client_secret = config["keycloak"]["api_client_secret"]
#     admin_client_id = config["keycloak"]["admin_client_id"]
#     admin_client_secret = config["keycloak"]["admin_client_secret"]
#
#
# class KeycloakIntrospectTokenValidator(IntrospectTokenValidator):
#     def introspect_token(self, token_string, host):
#         # url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/token/introspect"
#         url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/token/introspect"
#         data = {"token": token_string, "token_type_hint": "access_token"}
#         auth = (api_client_id, api_client_secret)
#         resp = requests.post(url, data=data, auth=auth)
#         return resp.json()
#
#
# current_token = None
#
#
# def get_keycloak_admin():
#     if not user_has_realm_role("admin"):
#         raise HTTPException(status_code=403, detail="Forbidden")
#
#     return KeycloakAdmin(
#         server_url=f"{keycloak_url}/",
#         realm_name=realm,
#         client_id=admin_client_id,
#         client_secret_key=admin_client_secret,
#         verify=True,
#     )
#
#
# def get_token_header(request: Request):
#     global current_token
#     auth_header = request.headers.get("Authorization")
#     host = request.headers.get("Host")
#     print(host)
#     if auth_header:
#         token_string = auth_header.split(" ")[1]
#         current_token = KeycloakIntrospectTokenValidator().introspect_token(
#             token_string, host
#         )
#         if current_token and "active" in current_token and current_token["active"]:
#             return current_token
#     raise HTTPException(status_code=401, detail="Invalid token")
#
#
# def user_has_realm_role(role):
#     return role in get_realm_roles()
#
#
# def get_realm_roles():
#     global current_token
#     if not current_token:
#         raise HTTPException(status_code=401, detail="Invalid token")
#     return current_token["realm_access"]["roles"]
#
#
# def require_role(role: str):
#     def dependency(token: dict = Depends(get_token_header)):
#         if not user_has_realm_role(role):
#             raise HTTPException(status_code=403, detail="Forbidden")
#         return token
#
#     return dependency
#
#
# def require_user_in_group(group_id: str, admin_allowed=False):
#     def dependency(token: dict = Depends(get_token_header)):
#         if not (admin_allowed and user_has_realm_role("admin")):
#             if not keycloak_user_in_group(group_id, token["sub"]):
#                 raise HTTPException(status_code=403, detail="User not in group")
#         return token
#
#     return dependency
#
#
# def keycloak_user_in_group(group_id, user_id, db = get_db()):
#     group = db.groups.find_one({"_id": group_id})
#     users = db.users.find({"_governance_id": {"$in": group["members"]}})
#     if any(user_id == user["_governance_id"] for user in users):
#         return True
#     return False
#
#
# def get_current_keycloak_id():
#     global current_token
#     return current_token["sub"]
