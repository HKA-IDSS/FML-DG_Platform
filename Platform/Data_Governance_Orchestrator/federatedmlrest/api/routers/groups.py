from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_codes
from pymongo.database import Database
from starlette.responses import Response

from federatedmlrest.api.DBConnection import get_db
from federatedmlrest.api.models.common import PyUUID
from federatedmlrest.keycloak_auth import get_current_user, require_role
from federatedmlrest.api import dependencies, errors
from federatedmlrest.api.models import group_models, user_models, ml_model_models, dataset_models
from federatedmlrest.api.tags import Tags
from federatedmlrest.lib import deleters, getters, updaters

from federatedmlrest.mongo import MongoDB, Collections

router = APIRouter(prefix='/groups', tags=[Tags.GROUPS])


@router.get(
    '',
    responses={
        http_codes.HTTP_200_OK: {'description': 'Returns a list with all groups.'}
    },
    response_model=list[group_models.Group],
    response_model_exclude_none=True,
)
async def get_all_groups(
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user),
) -> list[group_models.Group]:
    """Get all groups."""
    result: list[group_models.Group] = []
    user_id = token["sub"]
    all_groups = [group_models.Group(**g) for g in db[Collections.GROUPS].find({"_current": True, "_deleted": False})]
    # if user_has_realm_role("admin"):
    #     return all_groups
    # for group in all_groups:
    #     if keycloak_user_in_group(db, group.id, PyUUID(user_id)):
    #         result.append(group)
    # return result
    return all_groups


@router.get(
    '/{group_governance_id}',
    responses={
        http_codes.HTTP_200_OK: {'description': 'Returns the group.'},
        http_codes.HTTP_404_NOT_FOUND: {'description': 'The specified group was not found.'}
    },
    response_model=group_models.Group,
    response_model_exclude_none=True,
)
def get_group_with_version(
        group_governance_id: PyUUID,
        version: int = - 1,
        token: dict = Depends(get_current_user)
) -> group_models.Group:
    """Get a single group."""
    group = getters.find_group_governance(group_governance_id, version)
    return group


@router.get(
    '/{group_governance_id}/members',
    responses={
        http_codes.HTTP_200_OK: {'description': 'Returns a list with all members of a group.'}
    },
    response_model=list[user_models.User],
    response_model_exclude_none=True,
)
def get_all_members_of_group_version(
        group_governance_id: PyUUID,
        version: int = - 1,
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user),
) -> list[user_models.User]:
    """Get all members (users) of a group."""
    group = getters.find_group_governance(group_governance_id, version)
    members = MongoDB.resolve_governance_id_list(db, Collections.USERS, group.members)
    return members


@router.post(
    '',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'The group was created. Returns the new group.',
        },
    },
    response_model=group_models.Group,
    response_model_exclude_none=True,
)
async def add_group(
        new_group: group_models.AddGroup,
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user)
) -> group_models.Group:
    """Create a new group."""
    new_group_dict: dict[str, Any] = (group_models.Group(**new_group.dict())
                                      .dict(exclude_none=True, by_alias=True))
    new_group_dict["members"].append(PyUUID(token["sub"]))

    db[Collections.GROUPS].insert_one(new_group_dict)

    return group_models.Group(**new_group_dict)


@router.post(
    '/{group_governance_id}/add/{user_governance_id}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'The user was added to the group.'
        },
    },
    response_model=user_models.User,
    response_model_exclude_none=True,
)
def add_user_to_group(
        old_group: group_models.Group = Depends(dependencies.get_group),
        user_to_add: user_models.User = Depends(dependencies.get_user),
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user),
        # _=Depends(require_role("admin"))
) -> user_models.User:
    """Add a user to a group."""
    # user_to_add = getters.find_user(user_id, db)
    # old_group = getters.find_group_governance(group_id, db)
    all_groups = [group_models.Group(**g) for g in db[Collections.GROUPS].find({"_current": True})]
    group_of_user = [g for g in all_groups if user_to_add.id in g.members]

    if group_of_user or user_to_add.id in old_group.members:
        raise HTTPException(400, errors.USER_ALREADY_IN_GROUP)
    else:
        new_group_dict: dict = old_group.dict(exclude_none=True, by_alias=True)
        new_group_dict['_version'] += 1
        new_group_dict.pop('_id')
        new_group_dict["members"].append(user_to_add.governance_id)
        updaters.update_group(old_group, new_group_dict)
        # db[Collections.GROUPS].update_one(
        #     group.mongo_query(),
        #     {'$set': {'members': group.members}},
        # )
        return user_to_add


@router.delete(
    '/{group_governance_id}',
    status_code=http_codes.HTTP_204_NO_CONTENT,
    responses={
        http_codes.HTTP_204_NO_CONTENT: {
            'description': 'The group was successfully deleted.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The specified group was not found.',
        },
    },
    response_model_exclude_none=True,
)
def delete_group(
        group_governance_id: PyUUID,
        db: Database = Depends(get_db),
        # token: dict = Depends(get_current_user),  # This replaces @require_oauth
        _=Depends(require_role("admin"))  # This replaces @require_role
) -> Response:
    """Delete a group."""
    group = getters.find_group_governance(group_governance_id)
    for strategy_governance_id in group.strategies:
        strategy = getters.find_strategy_governance(strategy_governance_id)
        ml_models_assigned_to_strategy = \
            [ml_model_models.MLModel(**ml_model).governance_id
             for ml_model in db[Collections.ML_MODELS].find({"strategy_governance_id": strategy_governance_id})]
        for ml_model_governance_id in ml_models_assigned_to_strategy:
            deleters.delete_ml_model(ml_model_governance_id)

        dataset_assigned_to_strategy = \
            [dataset_models.Dataset(**dataset).governance_id
             for dataset in db[Collections.DATASETS].find({"strategy_governance_id": strategy_governance_id})]
        for dataset in dataset_assigned_to_strategy:
            deleters.delete_dataset(dataset)

        for qr_governance_id in strategy.quality_requirements:
            deleters.delete_quality_requirement(qr_governance_id)

        for qr_proposal_governance_id in strategy.quality_requirements_proposals:
            deleters.delete_proposal(qr_proposal_governance_id)

        for configuration_governance_id in strategy.configurations:
            deleters.delete_quality_requirement(configuration_governance_id)

        for configuration_proposal_governance_id in strategy.configuration_proposals:
            deleters.delete_proposal(configuration_proposal_governance_id)

        deleters.delete_strategy(strategy_governance_id)

    deleters.delete_group(group_governance_id)
    return Response(status_code=http_codes.HTTP_204_NO_CONTENT)


@router.put(
    '/governance_id/{group_governance_id}',
    status_code=http_codes.HTTP_200_OK,
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'The group was successfully changed. Returns the updated group.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The specified group was not found.',
        },
    },
    response_model=group_models.Group,
    response_model_exclude_none=True,
)
def update_group(
        new_group: group_models.AddGroup,
        old_group: group_models.Group = Depends(dependencies.get_group),
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user)
) -> group_models.Group:
    """Change group."""
    # old_group = getters.find_group_governance(old_group_id, db)
    dict_group = {"_governance_id": old_group.governance_id,
                  "_version": old_group.version + 1,
                  "_current": True,
                  "name": new_group.name,
                  "description": new_group.description,
                  "members": old_group.members,
                  "strategies": old_group.strategies}
    updaters.update_group(old_group, dict_group, db)

    return getters.find_group_governance(old_group.governance_id, db=db)
