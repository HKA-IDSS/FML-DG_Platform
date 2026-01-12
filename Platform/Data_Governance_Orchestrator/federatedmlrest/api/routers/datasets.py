from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi import status as http_codes
from pymongo.database import Database
from starlette.responses import Response

from federatedmlrest.api.DBConnection import get_db
from federatedmlrest.api.models.common import PyUUID
from federatedmlrest.keycloak_auth import get_current_user, require_role
from federatedmlrest.api import dependencies
from federatedmlrest.api.models import dataset_models
from federatedmlrest.api.tags import Tags
from federatedmlrest.lib import deleters, getters, validators, updaters
from federatedmlrest.mongo import Collections

router = APIRouter(
    prefix='/datasets',
    tags=[Tags.DATASETS],
)

@router.get(
    '',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a list of all datasets.',
        },
    },
    response_model=List[dataset_models.Dataset],
    response_model_exclude_none=True,
)
def get_all_datasets(
    db: Database = Depends(get_db),
    token: dict = Depends(get_current_user),
) -> List[dataset_models.Dataset]:
    """Get all datasets."""
    return [dataset_models.Dataset(**ds) for ds in db[Collections.DATASETS].find({"_current": True, "_deleted": False})]


@router.get(
    '/{dataset_governance_id}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns the Dataset.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The specified dataset was not found.',
        },
    },
    response_model=dataset_models.Dataset,
    response_model_exclude_none=True,
)
def get_dataset_by_id(
    dataset_governance_id: PyUUID,
    version: int = - 1,
    db: Database = Depends(get_db),
    token: dict = Depends(get_current_user)
) -> dataset_models.Dataset:
    """Get a single dataset."""
    dataset = getters.find_dataset_governance(dataset_governance_id, version, db)
    return dataset


@router.get(
    '/{dataset_governance_id}/features',
    responses={
        http_codes.HTTP_200_OK: {
            'descriptions': 'Returns a list of the features of the Dataset.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The specified dataset was not found.',
        },
    },
    response_model=List[dataset_models.Feature],
    response_model_exclude_none=True,
)
def get_all_features_of_dataset(
    dataset: dataset_models.Dataset = Depends(dependencies.get_dataset),
    token: dict = Depends(get_current_user)
) -> List[dataset_models.Feature]:
    """Get all features of a dataset."""
    return dataset.features

@router.post(
    '',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'The dataset was created. Returns the new dataset.',
        },
    },
    response_model=dataset_models.Dataset,
    response_model_exclude_none=True,
)
def add_dataset(
    new_dataset: dataset_models.AddDataset,
    db: Database = Depends(get_db),
    token: dict = Depends(get_current_user),
) -> dataset_models.Dataset:
    """Create a new dataset."""
    new_dataset_dict = dataset_models.Dataset(**new_dataset.dict()).dict(exclude_none=True, by_alias=True)
    # new_dataset_dict["proposer"] = get_current_keycloak_id()
    db[Collections.DATASETS].insert_one(new_dataset_dict)
    return dataset_models.Dataset(**new_dataset_dict)


@router.delete(
    '/{dataset_governance_id}',
    responses={
        http_codes.HTTP_204_NO_CONTENT: {
            'description': 'The Dataset was successfully deleted.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The Dataset is currently in use and thus cannot be deleted.',
        },
    },
    status_code=http_codes.HTTP_204_NO_CONTENT,
    response_model_exclude_none=True,
)
def delete_dataset(
    dataset_governance_id: PyUUID,
    token: dict = Depends(get_current_user),
) -> Response:
    """Delete a dataset."""
    # validators.check_for_dataset_references(db, dataset)
    deleters.delete_dataset(dataset_governance_id)
    return Response(status_code=http_codes.HTTP_204_NO_CONTENT)


@router.put(
    '/{dataset_governance_id}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'The features were successfully changed. Returns the updated Dataset.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The specified dataset was not found.',
        },
    },
    response_model=dataset_models.Dataset,
    response_model_exclude_none=True,
)
def update_features_of_dataset(
    new_dataset: dataset_models.AddDataset,
    old_dataset: dataset_models.Dataset = Depends(dependencies.get_dataset),
    db: Database = Depends(get_db),
    token: dict = Depends(get_current_user),
) -> dataset_models.Dataset:
    """Change features of a dataset."""
    new_dataset_dict = {"_governance_id": old_dataset.governance_id,
                        "_version": old_dataset.version + 1,
                        "_current": True,
                        "name": new_dataset.name,
                        "description": new_dataset.description,
                        "strategy_governance_id": new_dataset.strategy_governance_id,
                        "structured": new_dataset.structured,
                        "comments": new_dataset.comments,
                        'features': [f.dict(by_alias=True) for f in new_dataset.features]}
    # old_dataset.dict(exclude_none=True, by_alias=True)
    updaters.update_dataset(old_dataset, new_dataset_dict, db)

    return getters.find_dataset_governance(new_dataset_dict['_governance_id'], db=db)
