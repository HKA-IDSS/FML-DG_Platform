from typing import List, Dict, Any
import logging
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_codes
from pymongo import ReturnDocument
from pymongo.database import Database
from starlette.responses import Response

from federatedmlrest.api import dependencies, exceptions, errors
from federatedmlrest.api.dependencies import get_db
from federatedmlrest.api.models import user_models, organisation_models, group_models
from federatedmlrest.api.models.common import MongoID, MongoIDAndVersion, PyUUID
from federatedmlrest.api.tags import Tags
from federatedmlrest.keycloak_auth import get_current_user, require_role, get_keycloak_admin
from federatedmlrest.lib import deleters, getters, updaters
from federatedmlrest.mongo import Collections

router = APIRouter(
    prefix='/users',
    tags=[Tags.USERS],
    responses={
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The specified user was not found.',
        },
    },
)


@router.get(
    '',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a list with all users.',
        },
    }
)
def get_all_users(
        db: Database = Depends(get_db),
        # token: dict = Depends(get_current_user),
        _=Depends(require_role("admin"))
) -> List[user_models.User]:
    """Get a list of all users."""
    user_list = db[Collections.USERS].find({"_current": True, "_deleted": False})
    # for user in user_list:
    #     print(user)
    #     user.governance_id = dependencies.get_user_governance_id(str(user.governance_id))
    return [user_models.User(**u) for u in user_list]


@router.get(
    '/logged_user',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a single user.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'A resource (user) was not found.',
        },
    },
    response_model=user_models.User,
    response_model_exclude_none=True,
)
def get_logged_user(
        version: int = -1,
        token: dict = Depends(get_current_user)
) -> user_models.User:
    """Get a user by its id."""
    # if user_governance_id != PyUUID(get_current_keycloak_id()):
    #     raise HTTPException(403, errors.KEYCLOAK_CREATE_USER)
    user = getters.find_user_governance(PyUUID(get_current_user()["sub"]), version)
    return user

@router.get(
    '/{user_governance_id}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a single user.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'A resource (user) was not found.',
        },
    },
    response_model=user_models.User,
    response_model_exclude_none=True,
)
def get_user_by_id_and_version(
        user_governance_id: PyUUID,
        version: int = -1,
        db: Database = Depends(get_db),
        # token: dict = Depends(get_current_user),
        _=Depends(require_role("admin"))
) -> user_models.User:
    """Get a user by its id."""
    user = getters.find_user_governance(user_governance_id, version, db)
    return user


@router.get(
    '/only_name/{user_governance_id}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a single user.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'A resource (user) was not found.',
        },
    },
    response_model=user_models.UserName,
    response_model_exclude_none=True,
)
def get_username_by_governance_id(
        user_governance_id: PyUUID,
        token: dict = Depends(get_current_user)
        # _=Depends(require_role("admin"))
) -> user_models.UserName:
    """Get a username by its id."""
    name = getters.find_user_governance(user_governance_id).name
    return user_models.UserName(name=name)


@router.post(
    '',
    responses={
        http_codes.HTTP_201_CREATED: {
            'description': 'The user was created. Returns the new user.',
        },
    },
    response_model=user_models.User,
    response_model_exclude_none=True,
)
def create_user(
        new_user: user_models.AddUser,
        db: Database = Depends(get_db),
        # token: dict = Depends(get_current_user),
        _=Depends(require_role("admin"))
) -> user_models.User:
    """Creates a new user and returns it."""
    new_user_dict: Dict[str, Any] = user_models.User(**new_user.dict()).dict(exclude_none=True, by_alias=True)
    old_version_organisation = db[Collections.ORGANISATIONS].find_one(
        MongoIDAndVersion.get_current_document(new_user.organisation_id)
    )

    if not old_version_organisation:
        raise exceptions.OrganisationNotFoundException()

    try:
        new_kc_user = get_keycloak_admin().create_user({
            "username": new_user_dict.get("name"),
            "enabled": True,
            "credentials": [{
                "type": "password",
                "value": "password",
                "temporary": False
            }]
        })
        if not new_kc_user:
            raise HTTPException(400, 'User creation failed.')
        new_user_dict['_governance_id'] = UUID(new_kc_user)
    except Exception as e:
        print(f"Another exception: {e}")
        raise HTTPException(400, errors.KEYCLOAK_CREATE_USER)

    organisation = organisation_models.Organisation(**old_version_organisation)

    if new_user_dict['_governance_id'] not in organisation.users:
        organisation.users.append(new_user_dict['_governance_id'])

    new_organisation_dict = {
        '_governance_id': organisation.governance_id,
        '_version': organisation.version + 1,
        '_current': True,
        'name': organisation.name,
        'users': organisation.users
    }

    updaters.update_organisation(organisation, new_organisation_dict, db)

    db[Collections.USERS].insert_one(
        new_user_dict,
    )

    return user_models.User(**new_user_dict)


# @router.put(
#     '',
#     responses={
#         http_codes.HTTP_200_OK: {
#             'description': 'User information updated.',
#         },
#     },
#     response_model=user_models.User,
#     response_model_exclude_none=True,
# )
# def update_user(
#         new_user: user_models.AddUser,
#         user: user_models.User = Depends(dependencies.get_user),
#         db: Database = Depends(get_db),
#         token: dict = Depends(get_token_header),
#         _=Depends(require_role("admin"))
# ) -> user_models.User:
#     """Creates a new user and returns it."""
#     new_user_dict: Dict[str, Any] = user_models.User(**new_user.dict()).dict(exclude_none=True, by_alias=True)
#     try:
#         new_kc_user = get_keycloak_admin().create_user({
#             "username": new_user_dict.get("name"),
#             "enabled": True,
#             "credentials": [{
#                 "type": "password",
#                 "value": "password",
#                 "temporary": False
#             }]
#         })
#         if not new_kc_user:
#             raise HTTPException(400, 'User creation failed.')
#         new_user_dict['_id'] = UUID(new_kc_user)
#     except Exception as e:
#         raise HTTPException(400, errors.KEYCLOAK_CREATE_USER)
#
#     organisation = db[mongo.Collections.ORGANISATIONS].find_one(
#         MongoID.id_to_mongo_query(new_user.organisation_id)
#     )
#
#     if not organisation:
#         raise exceptions.OrganisationNotFoundException()
#
#     organisation = organisation_models.Organisation(**organisation)
#
#     # inserted_user = db[mongo.Collections.USERS].find_one_and_replace(
#     #     {'$or': [
#     #         {'_id': {'$eq': new_user_dict['_id']}},
#     #         {'name': {'$eq': new_user.name}},
#     #         {'description': {'$eq': new_user.description}}
#     #     ]},
#     #     new_user_dict,
#     #     upsert=True,
#     #     return_document=ReturnDocument.AFTER
#     # )
#
#     inserted_user = db[mongo.Collections.USERS].insert_one(
#         new_user_dict,
#     )
#
#     if not inserted_user.inserted_id in organisation.users:
#         organisation.users.append(inserted_user.inserted_id)
#         db[mongo.Collections.ORGANISATIONS].update_one(
#             organisation.mongo_query(),
#             {'$set': {'users': organisation.users}},
#         )
#
#     return user_models.User(**new_user_dict)

@router.delete(
    '/{user_governance_id}',
    status_code=http_codes.HTTP_204_NO_CONTENT,
    responses={
        http_codes.HTTP_204_NO_CONTENT: {
            'description': 'The user was successfully deleted.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The specified user was not found.',
        },
    },
    response_model_exclude_none=True,
)
def delete_user(
        user_governance_id: PyUUID,
        db: Database = Depends(get_db),
        # token: dict = Depends(get_current_user),
        _=Depends(require_role("admin"))
) -> Response:
    """Delete a user."""
    user = getters.find_user_governance(user_governance_id)

    organisation = getters.find_organisation_governance(user.organisation_id, db=db)
    new_organisation_dict = organisation.dict(exclude_none=True, by_alias=True)
    del new_organisation_dict["_id"]
    new_organisation_dict["_version"] += 1
    new_organisation_dict["users"].remove(user.governance_id)

    all_groups = [group_models.Group(**g) for g in db[Collections.GROUPS].find({"_current": True})]
    group_of_deleted_user = [g for g in all_groups if user.governance_id in g.members]

    for group in group_of_deleted_user:
        group = getters.find_group_governance(group.governance_id, db=db)
        new_group_dict = group.dict(exclude_none=True, by_alias=True)
        del new_group_dict["_id"]
        new_group_dict["_version"] += 1
        new_group_dict["members"].remove(user.governance_id)
        updaters.update_group(group, new_group_dict)

    deleters.delete_user(user.governance_id)
    updaters.update_organisation(organisation, new_organisation_dict)

    try:
        get_keycloak_admin().delete_user(user_id=str(user_governance_id))
    except Exception as e:
        raise HTTPException(400, errors.KEYCLOAK_DELETE_USER)

    return Response(status_code=http_codes.HTTP_204_NO_CONTENT)
