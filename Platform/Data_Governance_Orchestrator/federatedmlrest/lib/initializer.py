import logging
import os

from http.client import HTTPException
from uuid import uuid4, UUID

import yaml
from keycloak import KeycloakAdmin, KeycloakGetError
from federatedmlrest.api import errors
from federatedmlrest.api.DBConnection import get_db
from federatedmlrest.api.models.common import PyUUID
from federatedmlrest.keycloak_auth import get_current_user, require_role, require_user_in_group
from federatedmlrest.mongo import Collections


config_path = os.path.dirname(__file__) + "/../config.yml"
with open(config_path, "r") as file:
    config = yaml.safe_load(file)
    keycloak_url = config["keycloak"]["url"]
    realm = config["keycloak"]["realm"]
    api_client_id = config["keycloak"]["api_client_id"]
    api_client_secret = config["keycloak"]["api_client_secret"]
    admin_client_id = config["keycloak"]["admin_client_id"]
    admin_client_secret = config["keycloak"]["admin_client_secret"]

temp_admin = KeycloakAdmin(
    server_url=f"{keycloak_url}/",
    realm_name=realm,
    client_id=admin_client_id,
    client_secret_key=admin_client_secret
)


def create_starting_data():
    db = get_db()
    if db[Collections.ORGANISATIONS].find_one({"name": "governance_administration"}) is None:
        admin_org_governance_id = uuid4()
        db[Collections.ORGANISATIONS].insert_one({
            "_id": uuid4(),
            "name": "governance_administration",
            "_governance_id": admin_org_governance_id,
            "_version": 1,
            "_current": True,
            "_deleted": False
        })
        try:
            admin_governance_id = temp_admin.create_user({"username": "admin",
                                                          "credentials": [{"value": "hkakeycloak", "type": "password"}],
                                                          "groups": "admin",
                                                          "enabled": True})
            temp_admin.group_user_add(admin_governance_id, "admin")
        except KeycloakGetError as e:
            raise HTTPException(400, "Keycloak user already exists")
        db[Collections.USERS].insert_one({
            "_id": uuid4(),
            "_governance_id": admin_governance_id,
            "_version": 1,
            "_current": True,
            "_deleted": False,
            "name": "admin",
            "description": "Admin from the Governance Server",
            "organisation_id": admin_org_governance_id,
            "ip": None
        })

if __name__ == "__main__":
    create_starting_data()
