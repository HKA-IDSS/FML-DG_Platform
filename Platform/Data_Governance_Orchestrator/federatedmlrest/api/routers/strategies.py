from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import status as http_codes
from pymongo.database import Database
from starlette.responses import Response

from federatedmlrest.api.DBConnection import get_db
from federatedmlrest.api.models.common import PyUUID
from federatedmlrest.keycloak_auth import get_current_user, require_role, require_user_in_group
from federatedmlrest.api import dependencies
from federatedmlrest.api.models import group_models, strategy_models, ml_model_models, dataset_models
from federatedmlrest.api.tags import Tags
from federatedmlrest.lib import deleters, getters, updaters
from federatedmlrest.mongo import MongoDB
from federatedmlrest.mongo import Collections

router = APIRouter(
    prefix='/strategies',
    tags=[Tags.STRATEGIES],
    responses={
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The specified group was not found.',
        },
    },
)

def get_user_in_group(group_id: str, admin_allowed: bool = False):
    return require_user_in_group(group_id, admin_allowed)

@router.get(
    '/{strategy_governance_id}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns the strategy.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The group or strategy could not be found.',
        },
    },
    response_model=strategy_models.Strategy,
    response_model_exclude_none=True,
)
def get_strategy_by_id(
    strategy_governance_id: PyUUID,
    version: int = -1,
    token: dict = Depends(get_current_user),
    # _=Depends(get_user_in_group)
) -> strategy_models.Strategy:
    """Get a single strategy."""
    strategy = getters.find_strategy_governance(strategy_governance_id, version)
    group = getters.find_group_governance(strategy.belonging_group)
    get_user_in_group(str(group.governance_id))
    return strategy


@router.get(
    '/groups/{group_governance_id}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a list with all strategies of the group.',
        },
    },
    response_model=List[strategy_models.Strategy],
    response_model_exclude_none=True,
)
def get_all_strategies_of_group(
        group_governance_id: PyUUID,
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user)
) -> List[strategy_models.Strategy]:
    """Get all strategies."""
    group = getters.find_group_governance(group_governance_id)
    get_user_in_group(str(group.id))
    strategies = MongoDB.resolve_governance_id_list(
        db,
        Collections.STRATEGIES,
        group.strategies,
    )
    return [strategy_models.Strategy(**s) for s in strategies]


@router.post(
    '',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'The strategy was created. Returns the new strategy.',
        },
    },
    response_model=strategy_models.Strategy,
    response_model_exclude_none=True,
)
def add_strategy_to_group(
        new_strategy: strategy_models.AddStrategy,
        # group: group_models.Group = Depends(dependencies.get_group),
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user)
        # _=Depends(get_user_in_group)
) -> strategy_models.Strategy:
    """Create a new strategy."""
    new_strategy_dict = strategy_models.Strategy(**new_strategy.dict()).dict(exclude_none=True, by_alias=True)
    _ = get_user_in_group(new_strategy_dict["belonging_group"])
    group = getters.find_group_governance(new_strategy_dict["belonging_group"], db=db)
    db[Collections.STRATEGIES].insert_one(new_strategy_dict)
    dict_group = {"_governance_id": group.governance_id,
                  "_version": group.version + 1,
                  "_current": True,
                  "name": group.name,
                  "description": group.description,
                  "members": group.members,
                  "strategies": group.strategies}
    dict_group["strategies"].append(new_strategy_dict['_governance_id'])
    updaters.update_group(group, dict_group, db)
    return strategy_models.Strategy(**new_strategy_dict)


@router.delete(
    '/{strategy_governance_id}',
    status_code=http_codes.HTTP_204_NO_CONTENT,
    responses={
        http_codes.HTTP_204_NO_CONTENT: {
            'description': 'The strategy was successfully deleted.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The group or strategy could not be found.',
        },
    },
    response_model_exclude_none=True,
)
def delete_strategy(
        strategy_governance_id: PyUUID,
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user)
) -> Response:
    """Delete a strategy."""
    strategy = getters.find_strategy_governance(strategy_governance_id)
    group = getters.find_group_governance(strategy.belonging_group)
    _ = require_user_in_group(group)

    ml_models_assigned_to_strategy = \
        [ml_model_models.MLModel(**ml_model).governance_id
         for ml_model in db[Collections.ML_MODELS].find({"strategy_governance_id": strategy_governance_id})]
    for ml_model_governance_id in ml_models_assigned_to_strategy:
        deleters.delete_ml_model(ml_model_governance_id)

    dataset_assigned_to_strategy = \
        [dataset_models.Dataset(**dataset).governance_id
         for dataset in db[Collections.DATASETS].find({"strategy_governance_id": strategy_governance_id})]
    for dataset_governance_id in dataset_assigned_to_strategy:
        deleters.delete_dataset(dataset_governance_id)

    for qr_id in strategy.quality_requirements:
        deleters.delete_quality_requirement(qr_id)

    for qr_proposal_id in strategy.quality_requirements_proposals:
        deleters.delete_proposal(qr_proposal_id)

    for configuration_id in strategy.configurations:
        deleters.delete_quality_requirement(configuration_id)

    for configuration_proposal_id in strategy.configuration_proposals:
        deleters.delete_proposal(configuration_proposal_id)

    new_group = group.dict(exclude_none=True, by_alias=True)
    group.current = False
    del new_group["_id"]
    new_group["_current"] = True
    new_group["_version"] = group.version + 1
    new_group["strategies"].remove(strategy_governance_id)
    deleters.delete_strategy(strategy_governance_id)
    updaters.update_group(group, new_group)
    return Response(status_code=http_codes.HTTP_204_NO_CONTENT)


@router.put(
    '/{strategy_governance_id}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'The strategy was updated. Returns the new strategy.',
        },
    },
    response_model=strategy_models.Strategy,
    response_model_exclude_none=True,
)
def update_strategy_information(
        new_strategy_information: strategy_models.AddStrategy,
        # group: group_models.Group = Depends(dependencies.get_group),
        strategy: strategy_models.Strategy = Depends(dependencies.get_strategy),
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user)
        # _=Depends(get_user_in_group)
) -> strategy_models.Strategy:
    new_strategy_dict = strategy_models.Strategy(**new_strategy_information.dict()).dict(exclude_none=True, by_alias=True)
    _ = get_user_in_group(new_strategy_dict["belonging_group"])
    """Update Strategy"""
    new_strategy_information_dict = {
        "_governance_id": strategy.governance_id,
        "_version": strategy.version + 1,
        "_current": True,
        "name": new_strategy_information.name,
        "description": new_strategy_information.description,
        "comments": new_strategy_information.comments,
        "belonging_group": strategy.belonging_group,
        "configurations": strategy.configurations,
        "quality_requirements": strategy.quality_requirements,
        "configuration_proposals": strategy.configuration_proposals,
        "quality_requirements_proposals": strategy.quality_requirements_proposals
    }
    updaters.update_information_strategy(strategy, dict_strategy=new_strategy_information_dict, db=db)
    return strategy_models.Strategy(**new_strategy_information_dict)
