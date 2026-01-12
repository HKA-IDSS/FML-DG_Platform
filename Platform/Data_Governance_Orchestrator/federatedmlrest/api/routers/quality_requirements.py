from typing import List, Optional
from uuid import UUID

import fastapi
from fastapi import Depends
from fastapi import status as http_codes
from pymongo.database import Database
from starlette.responses import Response

from federatedmlrest.api import dependencies, exceptions
from federatedmlrest.api.DBConnection import get_db
from federatedmlrest.api.models import quality_requirements_models as qrm
from federatedmlrest.api.models import proposal_models
from federatedmlrest.api.models import strategy_models
from federatedmlrest.api.models.common import PyUUID
from federatedmlrest.api.tags import Tags
from federatedmlrest.keycloak_auth import get_current_user
from federatedmlrest.lib import deleters, validators, getters
from federatedmlrest.mongo import MongoDB

from federatedmlrest.mongo import Collections

router = fastapi.APIRouter(
    prefix='/strategies/{strategy_governance_id}/quality_requirements',
    tags=[Tags.QUALITY_REQUIREMENTS],
    responses={
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The group or strategy could not be found.',
        },
    },
)


@router.get(
    '',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns a list of all quality requirement objects.'
        },
    },
    response_model=List[qrm.QualityRequirement],
    response_model_exclude_none=True,
)
def get_all_quality_requirements_of_strategy(
    strategy_governance_id: PyUUID,
    version: int = -1,
    name: Optional[str] = fastapi.Query(None, description='Filter by name'),
    token: dict = Depends(get_current_user),
    db: Database = Depends(get_db),
) -> List[qrm.QualityRequirement]:
    """Get all quality requirements."""
    strategy = getters.find_strategy_governance(strategy_governance_id, version)
    all_qrs = [
        getters.find_quality_requirement(qrm.QualityRequirement(**qr).id)
        for qr in MongoDB.resolve_id_list(db, Collections.QUALITY_REQUIREMENTS, strategy.quality_requirements)
    ]

    if not name:
        return all_qrs

    filtered_qrs = list(
        filter(
            lambda qr: qr.name == name,
            all_qrs,
        ),
    )

    return filtered_qrs


@router.get(
    '/{quality_requirement_id}',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'Returns the quality requirement.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The group, strategy or quality requirement could not be found.',
        },
    },
    response_model=qrm.QualityRequirement,
    response_model_exclude_none=True,
)
def get_quality_requirement_of_strategy_by_id(
    quality_requirement: qrm.QualityRequirement = Depends(dependencies.get_quality_requirement_id),
    token: dict = Depends(get_current_user)
) -> qrm.QualityRequirement:
    """Get a single quality requirement."""
    return quality_requirement


# @router.post(
#     '',
#     responses={
#         http_codes.HTTP_200_OK: {
#             'description': 'The quality requirement was created. Returns the new quality requirement.',
#         },
#         http_codes.HTTP_404_NOT_FOUND: {
#             'description': 'A resource could not be found (Group or Strategy).',
#         },
#     },
#     response_model=qrm.QualityRequirement,
#     response_model_exclude_none=True,
# )
# def add_quality_requirement_proposal(
#     new_quality_requirement: proposal_models.AddProposal,
#     strategy: strategy_models.Strategy = Depends(dependencies.get_strategy),
#     db: Database = Depends(get_db),
# ) -> qrm.QualityRequirement:
#     """Add a new quality requirement."""
#     # todo: set status of qr to unproposed or smthn like that
#     # new_qr_dict = qrm.QualityRequirement(**new_quality_requirement.dict()).dict(exclude_none=True,by_alias=True)
# #   inserted_quality_requirement = db[Collections.QUALITY_REQUIREMENTS].insert_one(new_qr_dict)
# #   strategy.quality_requirements.append(inserted_quality_requirement.inserted_id)
# #     db[Collections.PROPOSALS].add(
# #         {'_governance_id': strategy.governance_id, '_current': True},
# #         {'$set': {'quality_requirements': strategy.quality_requirements}}
# #     )
#     new_proposal_dict = qrm.QualityRequirementProposal(**new_quality_requirement.dict()).dict(
#         exclude_none=True, by_alias=True
#     )
#     inserted_proposal = db[Collections.PROPOSALS].insert_one(new_proposal_dict)
#
#     return inserted_proposal
#     # return dependencies.get_quality_requirement(
#     #     strategy=strategy, quality_requirement_id=qrm.QualityRequirement(**new_qr_dict).id, db=db,
#     # )


@router.delete(
    '/{quality_requirement_id}',
    status_code=http_codes.HTTP_204_NO_CONTENT,
    responses={
        http_codes.HTTP_204_NO_CONTENT: {
            'description': 'The quality requirement was successfully deleted.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'The group, strategy or quality requirement could not be found.',
        },
    },
    response_model_exclude_none=True,
)
def delete_quality_requirements_from_strategy(
        strategy: strategy_models.Strategy = Depends(dependencies.get_strategy),
        quality_requirement: qrm.QualityRequirement = Depends(dependencies.get_quality_requirement),
        token: dict = Depends(get_current_user),
        db: Database = Depends(get_db),
) -> Response:
    """Delete a quality requirement."""
    deleters.delete_quality_requirement(db, strategy, quality_requirement.id)
    return Response(status_code=http_codes.HTTP_204_NO_CONTENT)


# @router.put(
#     '/{quality_requirement_id}',
#     responses={
#         http_codes.HTTP_200_OK: {
#             'description': 'The quality requirement was successfully changed. Returns the updated quality requirement.',
#         },
#         http_codes.HTTP_404_NOT_FOUND: {
#             'description': 'A resource could not be found (Group, Strategy, or quality requirement)',
#         },
#     },
#     response_model=qrm.QualityRequirement,
#     response_model_exclude_none=True,
# )
# def update_quality_requirement(
#     new_quality_requirement: qrm.UpdateQualityRequirements = fastapi.Body(...),
#     quality_requirement: qrm.QualityRequirement = Depends(dependencies.get_quality_requirement),
#     db: Database = Depends(get_db),
# ) -> qrm.QualityRequirement:
#     """Change a quality requirement's attributes."""
#     validators.object_exists(
#         db[Collections.QUALITY_REQUIREMENTS],
#         quality_requirement.id,
#         exceptions.QualityRequirementNotFoundException(),
#     )
#     for name, value, in new_quality_requirement.dict(exclude_none=True).items():
#         setattr(quality_requirement, name, value)
#     db[Collections.QUALITY_REQUIREMENTS].update_one(
#         quality_requirement.mongo_query(),
#         {'$set': quality_requirement.dict(by_alias=True)},
#     )
#
#     return getters.find_quality_requirement(quality_requirement.id, db=db)


# todo: method change status of qr