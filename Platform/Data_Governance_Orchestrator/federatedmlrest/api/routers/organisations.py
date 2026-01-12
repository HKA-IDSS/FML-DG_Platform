from typing import List, Dict, Any, Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Path
from fastapi import status as http_codes
from pymongo.database import Database
from starlette.responses import Response

from federatedmlrest.api.DBConnection import get_db
from federatedmlrest.api.models.common import MongoIDAndVersion, PyUUID
from federatedmlrest.keycloak_auth import get_current_user, require_role
from federatedmlrest.api import dependencies
from federatedmlrest.api.models import organisation_models
from federatedmlrest.api.tags import Tags
from federatedmlrest.lib import deleters, getters
from federatedmlrest.mongo import Collections

router = APIRouter(
    prefix='/organisations',
    tags=[Tags.ORGANISATIONS],
    responses={
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The specified organisation was not found.',
        },
    },
)


@router.get(
    '',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a list with all organisations.',
        },
    }
)
def get_all_organisations(
        db: Database = Depends(get_db),
        # token: dict = Depends(get_current_user),
        _=Depends(require_role("admin"))
) -> List[organisation_models.Organisation]:
    """Get a list of all users."""
    return [organisation_models.Organisation(**o) for o in db[Collections.ORGANISATIONS].find({"_current": True})]


# @router.get(
#     '/{organisation_governance_id}',
#     responses={
#         http_codes.HTTP_200_OK: {
#             'description': 'Returns a single organisation.',
#         },
#         http_codes.HTTP_404_NOT_FOUND: {
#             'description': 'A resource (organisation) was not found.',
#         },
#     },
#     response_model=organisation_models.Organisation,
#     response_model_exclude_none=True,
# )
# def get_organisation_by_id(
#         organisation: organisation_models.Organisation = Depends(dependencies.get_organisation),
#         token: dict = Depends(get_token_header),
#         _=Depends(require_role("admin"))
# ) -> organisation_models.Organisation:
#     """Get an organisation by its id."""
#     return organisation


@router.get(
    '/{organisation_governance_id}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a single organisation.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'A resource (organisation) was not found.',
        },
    },
    response_model=organisation_models.Organisation,
    response_model_exclude_none=True,
)
def get_organisation_by_id_and_version(
        organisation_governance_id: Annotated[PyUUID, Path(title="Governance id of the organization")],
        version: int = - 1,
        db: Database = Depends(get_db),
        # token: dict = Depends(get_current_user),
        _=Depends(require_role("admin"))
) -> organisation_models.Organisation:
    """Get an organisation by its id."""
    organisation = getters.find_organisation_governance(organisation_governance_id, version, db)
    return organisation


@router.post(
    '',
    responses={
        http_codes.HTTP_201_CREATED: {
            'description': 'The organisation was created. Returns the new organisation.',
        },
    },
    response_model=organisation_models.Organisation,
    response_model_exclude_none=True,
)
def create_organisation(
        new_organisation: organisation_models.AddOrganisation,
        db: Database = Depends(get_db),
        # token: dict = Depends(get_current_user),
        _=Depends(require_role("admin"))
) -> organisation_models.Organisation:
    """Creates a new organisation and returns it."""
    new_organisation_dict: Dict[str, Any] = (organisation_models.Organisation(**new_organisation.dict())
                                             .dict(exclude_none=True, by_alias=True))
    db[Collections.ORGANISATIONS].insert_one(new_organisation_dict)
    return organisation_models.Organisation(**new_organisation_dict)


@router.delete(
    '/{organisation_governance_id}',
    status_code=http_codes.HTTP_204_NO_CONTENT,
    responses={
        http_codes.HTTP_204_NO_CONTENT: {
            'description': 'The organisation was successfully deleted.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The specified organisation was not found.',
        },
    },
    response_model_exclude_none=True,
)
def delete_organisation(
        organisation: organisation_models.Organisation = Depends(dependencies.get_organisation),
        db: Database = Depends(get_db),
        # token: dict = Depends(get_current_user),
        _=Depends(require_role("admin"))
) -> Response:
    """Delete a organisation."""
    for user in organisation.users:
        deleters.delete_user(user)
    deleters.delete_organisation(organisation.id, db)
    return Response(status_code=http_codes.HTTP_204_NO_CONTENT)
