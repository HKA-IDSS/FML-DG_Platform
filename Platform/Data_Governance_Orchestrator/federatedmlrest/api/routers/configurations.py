from typing import List, Optional

import fastapi
from fastapi import Depends
from fastapi import status as http_codes
from pymongo.database import Database
from starlette.responses import Response

from federatedmlrest.api.DBConnection import get_db
from federatedmlrest.keycloak_auth import get_current_user, require_role, require_user_in_group
from federatedmlrest.api import dependencies, exceptions
from federatedmlrest.api.models import config_models, strategy_models
from federatedmlrest.api.models.common import PyUUID
from federatedmlrest.api.tags import Tags
from federatedmlrest.lib import deleters, getters, validators, updaters
from federatedmlrest.mongo import MongoDB, Collections

router = fastapi.APIRouter(
    prefix='/strategies/{strategy_governance_id}/configurations',
    tags=[Tags.CONFIGURATIONS],
    responses={
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The group or strategy could not be found.',
        },
    },
)


def get_user_in_group(group_id: str, admin_allowed: bool = False):
    return require_user_in_group(group_id, admin_allowed)


@router.get(
    '',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a list of all configurations.'
        },
    },
    response_model=List[config_models.Configuration],
    response_model_exclude_none=True,
)
def get_all_configurations_of_strategy(
        strategy_governance_id: PyUUID,
        version: int = -1,
        ml_name: Optional[str] = fastapi.Query(None, description='Filter by ml model name'),
        dataset_name: Optional[str] = fastapi.Query(None, description='Filter by dataset name'),
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user)
) -> List[config_models.Configuration]:
    """Get all configurations."""
    strategy = getters.find_strategy_governance(strategy_governance_id, db=db, version=version)
    group = getters.find_group_governance(strategy.belonging_group)
    _ = Depends(get_user_in_group(group_id=str(group.governance_id))),

    all_configs = [
        getters.find_config(config) for config in strategy.configurations
    ]

    if not ml_name and not dataset_name:
        return all_configs

    filtered_configs = list(
        filter(
            lambda config: config.ml_model.name == ml_name or config.dataset.name == dataset_name,
            all_configs,
        ),
    )

    return filtered_configs


@router.get(
    '/{configuration_id}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns the configuration.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The group, strategy or configuration could not be found.',
        },
    },
    response_model=config_models.Configuration,
    response_model_exclude_none=True,
)
def get_configuration_of_strategy_by_id(
        configuration: config_models.Configuration = Depends(dependencies.get_configuration),
        token: dict = Depends(get_current_user),
        _=Depends(get_user_in_group),
) -> config_models.Configuration:
    """Get a single configuration."""
    return configuration

#
# @router.post(
#     '',
#     responses={
#         http_codes.HTTP_200_OK: {
#             'description': 'The configuration was created. Returns the new configuration.',
#         },
#         http_codes.HTTP_404_NOT_FOUND: {
#             'description': 'A resource could not be found (Group, Strategy, ML Model or Dataset).',
#         },
#     },
#     response_model=config_models.Configuration,
#     response_model_exclude_none=True,
# )
# def add_configuration_to_strategy(
#         new_config: config_models.AddConfiguration,
#         old_strategy: strategy_models.Strategy = Depends(dependencies.get_strategy),
#         db: Database = Depends(get_db),
#         token: dict = Depends(get_token_header),
#         _=Depends(get_user_in_group),
# ) -> config_models.Configuration:
#     """Add a new configuration."""
#     validators.object_with_version_exists(
#         db[Collections.ML_MODELS],
#         new_config.ml_model_id,
#         new_config.ml_model_version,
#         exceptions.MLModelNotFoundException(),
#     )
#     validators.object_with_version_exists(
#         db[Collections.DATASETS],
#         new_config.dataset_id,
#         new_config.dataset_version,
#         exceptions.DatasetNotFoundException(),
#     )
#
#     new_config_dict = config_models.Configuration(**new_config.dict()).dict(exclude_none=True, by_alias=True)
#
#     inserted_config = db[Collections.CONFIGURATIONS].insert_one(new_config_dict)
#     new_strategy_dict = old_strategy.dict(exclude_none=True, by_alias=True)
#     new_strategy_dict["configurations"].append(inserted_config.inserted_id)
#     new_strategy_dict["_version"] += 1
#     new_strategy_dict.pop("_id")
#     updaters.update_information_strategy(db, old_strategy, new_strategy_dict)
#
#     return dependencies.get_configuration_extra(config_models.Configuration(**new_config_dict), db=db)


@router.delete(
    '/{configuration_id}',
    status_code=http_codes.HTTP_204_NO_CONTENT,
    responses={
        http_codes.HTTP_204_NO_CONTENT: {
            'description': 'The configuration was successfully deleted.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The group, strategy or configuration could not be found.',
        },
    },
    response_model_exclude_none=True,
)
def delete_configurations_from_strategy(
        strategy: strategy_models.Strategy = Depends(dependencies.get_strategy),
        config_id: config_models.Configuration = Depends(dependencies.get_configuration),
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user),
        _=Depends(get_user_in_group),
) -> Response:
    """Delete a configuration."""
    deleters.delete_config(db, strategy, config_id)
    return Response(status_code=http_codes.HTTP_204_NO_CONTENT)


@router.put(
    '/{configuration_id}/mlmodel',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'The configuration was successfully changed. Returns the updated configuration.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'A resource could not be found (Group, Strategy, Configuration, or ML Model)',
        },
    },
    response_model=config_models.Configuration,
    response_model_exclude_none=True,
)
def update_ml_model_of_configuration(
        ml_model_id: PyUUID = Depends(dependencies.get_ml_model_governance_id),
        config: config_models.Configuration = Depends(dependencies.get_configuration),
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user),
        _=Depends(get_user_in_group),
) -> config_models.Configuration:
    """Change a configuration's ml model."""
    validators.object_exists(
        db[Collections.ML_MODELS],
        ml_model_id,
        exceptions.MLModelNotFoundException(),
    )
    db[Collections.CONFIGURATIONS].update_one(
        config.mongo_query(),
        {'$set': {'ml_model_id': ml_model_id}},
    )

    return getters.find_config(config.id, db=db)


@router.put(
    '/{configuration_id}/dataset',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'The configuration was successfully changed. Returns the updated configuration.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'A resource could not be found (Group, Strategy, Configuration, or Dataset)',
        },
    },
    response_model=config_models.Configuration,
    response_model_exclude_none=True,
)
def update_dataset_of_configuration(
        dataset_id: PyUUID = Depends(dependencies.get_dataset_governance_id),
        config: config_models.Configuration = Depends(dependencies.get_configuration),
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user),
        _=Depends(get_user_in_group),
) -> config_models.Configuration:
    """Change a configuration's dataset."""
    validators.object_exists(
        db[Collections.DATASETS],
        dataset_id,
        exceptions.DatasetNotFoundException(),
    )
    db[Collections.CONFIGURATIONS].update_one(
        config.mongo_query(),
        {'$set': {'dataset_id': dataset_id}},
    )

    return getters.find_config(config.id, db=db)

# @router.get(
#     '/{configuration_id}/dataset',
#     responses={
#         http_codes.HTTP_200_OK: {
#             'description': 'The configuration was successfully changed. Returns the updated configuration.',
#         },
#         http_codes.HTTP_404_NOT_FOUND: {
#             'description': 'A resource could not be found (Group, Strategy, Configuration, or Dataset)',
#         },
#     },
#     response_model=config_models.Configuration,
#     response_model_exclude_none=True,
# )
# def get_configuration_to_run(config_id):
#     aggregation_process = "FedAvg"
#
#     if model == "xgboost":
#         aggregation_process = "FedXGB"
