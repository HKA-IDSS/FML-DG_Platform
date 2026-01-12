from typing import List, Union
from uuid import UUID

import fastapi
from fastapi import Depends
from fastapi import status as http_codes
from pymongo.database import Database
from starlette.responses import Response

from federatedmlrest.api.DBConnection import get_db
from federatedmlrest.api.models.common import PyUUID
from federatedmlrest.api.models.ml_model_models import MLP, XGBoost, Custom
from federatedmlrest.keycloak_auth import get_current_user, require_role
from federatedmlrest.api import dependencies, exceptions
from federatedmlrest.api.models import ml_model_models
from federatedmlrest.api.tags import Tags
from federatedmlrest.lib import deleters, getters, validators, updaters
from federatedmlrest.mongo import Collections

router = fastapi.APIRouter(
    prefix='/ml-models',
    tags=[Tags.ML_MODELS],
)

#TODO I think there is an error without the /, because the calls from the frontend are inconsistent across routes.
# Double check another time.
@router.get(
    '/',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a list with all ML Models.',
        },
    },
    response_model=List[ml_model_models.MLModel],
    response_model_exclude_none=True,
)
def get_all_ml_models(
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user),
) -> List[ml_model_models.MLModel]:
    """Get all ml models."""
    return [ml_model_models.MLModel(**ml) for ml in db[Collections.ML_MODELS].find({"_current": True, "_deleted": False})]


@router.get(
    '/{ml_model_governance_id}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a list with all ML Models.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The specified ml model was not found.'
        },
    },
    response_model=ml_model_models.MLModel,
    response_model_exclude_none=True,
)
def get_ml_model_by_id(
        ml_model_governance_id: PyUUID,
        version: int = - 1,
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user),
) -> ml_model_models.MLModel:
    """Get a single ml model."""
    ml_model = getters.find_ml_model_governance(ml_model_governance_id, version, db)
    return ml_model

@router.get(
    '/default_model/{model_type}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a list with all ML Models.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The specified ml model was not found.'
        },
    },
    response_model=Union[MLP, XGBoost, Custom],
    response_model_exclude_none=True,
)
def get_default_model(
        model_type: str,
        token: dict = Depends(get_current_user),
) -> Union[MLP, XGBoost, Custom]:
    """Get a single ml model."""
    if model_type not in ['mlp', 'xgboost', 'custom']:
        raise exceptions.ModelTypeNotFound()
    elif model_type == 'mlp':
        return MLP()
    elif model_type == 'xgboost':
        return XGBoost()
    else:
        return Custom()


@router.post(
    '',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'The ML Model was created. Returns the new ML Model.',
        },
    },
    response_model=ml_model_models.MLModel,
    response_model_exclude_none=True,
)
def add_ml_model(
        new_ml_model: ml_model_models.AddMLModel,
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user),
) -> ml_model_models.MLModel:
    """Create a new ml model."""

    new_ml_model_dict = ml_model_models.MLModel(**new_ml_model.dict()).dict(exclude_none=True, by_alias=True)
    # new_ml_model_dict["proposer"] = PyUUID(get_current_keycloak_id())
    db[Collections.ML_MODELS].insert_one(new_ml_model_dict)
    return ml_model_models.MLModel(**new_ml_model_dict)


@router.put(
    '/{ml_model_governance_id}',
    status_code=http_codes.HTTP_200_OK,
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'The ml model was successfully changed. Returns the updated ml model.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The specified ml model was not found.',
        },
    },
    response_model=ml_model_models.MLModel,
    response_model_exclude_none=True,
)
def update_ml_model(
        new_ml_model: ml_model_models.AddMLModel,
        ml_model: ml_model_models.MLModel = Depends(dependencies.get_ml_model),
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user),
) -> ml_model_models.MLModel:
    """Change ML Model."""
    # new_ml_model_dict = ml_model_models.MLModel(**new_ml_model.dict()).dict(exclude_none=True, by_alias=True)

    new_model_information_dict = {
        "_governance_id": ml_model.governance_id,
        "_version": ml_model.version + 1,
        "_current": True,
        "name": new_ml_model.name,
        "description": new_ml_model.description,
        "strategy_governance_id": new_ml_model.strategy_governance_id,
        "model": new_ml_model.model,
        "comments": new_ml_model.comments,
    }
    updaters.update_ml_model(ml_model, new_model_information_dict, db)

    return getters.find_ml_model_governance(ml_model.governance_id, db=db)


@router.delete(
    '/{ml_model_governance_id}',
    status_code=http_codes.HTTP_204_NO_CONTENT,
    responses={
        http_codes.HTTP_204_NO_CONTENT: {
            'description': 'The ML Model was successfully deleted.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The specified ml model was not found.',
        },
        http_codes.HTTP_409_CONFLICT: {
            'description': 'The ML Model is currently in use and thus cannot be deleted.',
        },
    },
    response_model_exclude_none=True,
)
def delete_ml_model(
        ml_model_governance_id: PyUUID,
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user),
) -> Response:
    """Delete the ml model."""
    # validators.check_for_ml_model_references(db, ml_model)
    deleters.delete_ml_model(ml_model_governance_id)
    return Response(status_code=http_codes.HTTP_204_NO_CONTENT)
