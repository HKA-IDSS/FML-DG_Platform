import os

import requests
import yaml
from authlib.oauth2.rfc7662 import IntrospectTokenValidator
from fastapi import HTTPException, Depends, Request
from keycloak import KeycloakAdmin

from federatedmlrest.api.DBConnection import get_db
from federatedmlrest.mongo import MongoDB

config_path = os.path.dirname(__file__) + "/config.yml"
with open(config_path, "r") as file:
    config = yaml.safe_load(file)
    keycloak_url = config["keycloak"]["url"]
    keycloak_introspect_url = config["keycloak"]["url"]
    realm = config["keycloak"]["realm"]
    api_client_id = config["keycloak"]["api_client_id"]
    api_client_secret = config["keycloak"]["api_client_secret"]
    admin_client_id = config["keycloak"]["admin_client_id"]
    admin_client_secret = config["keycloak"]["admin_client_secret"]


class KeycloakIntrospectTokenValidator(IntrospectTokenValidator):
    def introspect_token(self, token_string, host):
        # url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/token/introspect"
        url = f"{keycloak_url}/realms/{realm}/protocol/openid-connect/token/introspect"
        data = {"token": token_string, "token_type_hint": "access_token"}
        auth = (api_client_id, api_client_secret)
        resp = requests.post(url, data=data, auth=auth)
        return resp.json()


current_token = None


def get_keycloak_admin():
    if not user_has_realm_role("admin"):
        raise HTTPException(status_code=403, detail="Forbidden")

    return KeycloakAdmin(
        server_url=f"{keycloak_url}/",
        realm_name=realm,
        client_id=admin_client_id,
        client_secret_key=admin_client_secret,
        verify=True,
    )


def get_token_header(request: Request):
    global current_token
    auth_header = request.headers.get("Authorization")
    host = request.headers.get("Host")
    print(host)
    if auth_header:
        token_string = auth_header.split(" ")[1]
        current_token = KeycloakIntrospectTokenValidator().introspect_token(
            token_string, host
        )
        if current_token and "active" in current_token and current_token["active"]:
            return current_token
    raise HTTPException(status_code=401, detail="Invalid token")


def user_has_realm_role(role):
    return role in get_realm_roles()


def get_realm_roles():
    global current_token
    if not current_token:
        raise HTTPException(status_code=401, detail="Invalid token")
    return current_token["realm_access"]["roles"]


def require_role(role: str):
    def dependency(token: dict = Depends(get_token_header)):
        if not user_has_realm_role(role):
            raise HTTPException(status_code=403, detail="Forbidden")
        return token

    return dependency


def require_user_in_group(group_id: str, admin_allowed=False):
    def dependency(token: dict = Depends(get_token_header)):
        if not (admin_allowed and user_has_realm_role("admin")):
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


def get_current_keycloak_id():
    global current_token
    return current_token["sub"]
