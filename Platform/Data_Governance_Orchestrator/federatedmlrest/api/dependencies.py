import secrets

import fastapi
from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from pymongo.database import Database

from federatedmlrest.api import exceptions
from federatedmlrest.api.DBConnection import get_db
from federatedmlrest.api.exceptions import (
    UserUnauthorizedException,
    VotePriorityAlreadyExistsException,
)
from federatedmlrest.api.models import (
    config_models,
    dataset_models,
    group_models,
    ml_model_models,
    proposal_models,
    user_models,
    organisation_models,
)
from federatedmlrest.api.models import quality_requirements_models as qrm
from federatedmlrest.api.models import strategy_models
from federatedmlrest.api.models.common import PyUUID
from federatedmlrest.lib import getters
from federatedmlrest.mongo import Collections


def get_username_basic_auth(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    """Validate that credentials are correct and return username."""
    current_username_bytes = credentials.username.encode("utf8")
    correct_username_bytes = b"your_username_here"
    is_correct_username = secrets.compare_digest(
        current_username_bytes, correct_username_bytes
    )
    current_password_bytes = credentials.password.encode("utf8")
    correct_password_bytes = b"your_password_here"
    is_correct_password = secrets.compare_digest(
        current_password_bytes, correct_password_bytes
    )
    if not (is_correct_username and is_correct_password):
        raise UserUnauthorizedException()

    return credentials.username


def transform_to_pyuuid(uuid: str) -> PyUUID:
    """Validate if string is UUID."""
    return PyUUID(uuid)


def get_organisation_governance_id(
        organisation_governance_id: str = fastapi.Path(
            ...,
            description="The governance ID of the organisation.",
        ),
) -> PyUUID:
    """Get validated organisation id."""
    return transform_to_pyuuid(organisation_governance_id)


def get_organisation(
        organisation_governance_id: PyUUID = Depends(get_organisation_governance_id),
        db: Database = Depends(get_db),
) -> organisation_models.Organisation:
    return getters.find_organisation_governance(organisation_governance_id, db=db)


def get_group_governance_id(
        group_governance_id: str = fastapi.Path(
            ...,
            description="The governance ID of the group.",
        ),
) -> PyUUID:
    """Get validated group_id."""
    return transform_to_pyuuid(group_governance_id)


def get_group(
        group_governance_id: PyUUID = Depends(get_group_governance_id),
        db: Database = Depends(get_db),
) -> group_models.Group:
    """Get group object from db."""
    return getters.find_group_governance(group_governance_id, db=db)


def get_user_governance_id(
        user_governance_id: str = fastapi.Path(
            ...,
            description="The ID of the user.",
        ),
) -> PyUUID:
    """Get validated user id."""
    return transform_to_pyuuid(user_governance_id)


def get_user(
        user_governance_id: PyUUID = Depends(get_user_governance_id),
        db: Database = Depends(get_db)
) -> user_models.User:
    return getters.find_user_governance(user_governance_id, db=db)


def check_if_member(group, user_governance_id, db):
    if user_governance_id not in group.members:
        raise exceptions.MemberNotFoundException


def get_strategy_governance_id(
        strategy_governance_id: str = fastapi.Path(
            ...,
            description="The ID of the strategy.",
        ),
) -> PyUUID:
    """Get validated member_id."""
    return transform_to_pyuuid(strategy_governance_id)


def get_strategy(
        # group: group_models.Group = Depends(get_group),
        strategy_governance_id: PyUUID = Depends(get_strategy_governance_id),
        db: Database = Depends(get_db),
) -> strategy_models.Strategy:
    """Get dataset object from db."""
    # if strategy_id not in group.strategies:
    #     raise exceptions.StrategyNotFoundException()

    return getters.find_strategy_governance(strategy_governance_id, db=db)


def get_dataset_governance_id(
        dataset_governance_id: str = fastapi.Path(
            ...,
            description="The governance_id of the Dataset.",
        )
) -> PyUUID:
    """Get Validated dataset id."""
    return transform_to_pyuuid(dataset_governance_id)


def get_dataset(
        dataset_governance_id: PyUUID = Depends(get_dataset_governance_id),
        db: Database = Depends(get_db),
) -> dataset_models.Dataset:
    """Get dataset object from db."""
    return getters.find_dataset_governance(dataset_governance_id, db=db)


def get_ml_model_governance_id(
        ml_model_governance_id: str = fastapi.Path(
            ...,
            description="The governance_id of the Ml Model.",
        )
) -> PyUUID:
    """Get Validated ml model id."""
    return transform_to_pyuuid(ml_model_governance_id)


def get_ml_model(
        ml_model_governance_id: PyUUID = Depends(get_ml_model_governance_id),
        db: Database = Depends(get_db),
) -> ml_model_models.MLModel:
    """Get ml model object from db."""
    return getters.find_ml_model_governance(ml_model_governance_id, db=db)


def get_proposal_id(
        proposal_id: str = fastapi.Path(
            ...,
            description="The ID of the proposal.",
        ),
) -> PyUUID:
    """Get validated proposal id."""
    return transform_to_pyuuid(proposal_id)


def get_proposal(
        proposal_id: PyUUID = Depends(get_proposal_id),
        db: Database = Depends(get_db),
) -> proposal_models.Proposal:
    """Get proposal object from db."""

    return getters.find_proposal(proposal_id, db=db)


def get_config_id(
        configuration_id: str = fastapi.Path(
            ...,
            description="The ID of the proposal.",
        ),
) -> PyUUID:
    """Get validated proposal id."""
    return transform_to_pyuuid(configuration_id)


def get_configuration(
        strategy: strategy_models.Strategy = Depends(get_strategy),
        configuration_id: config_models.Configuration = Depends(get_config_id),
        db: Database = Depends(get_db)
) -> config_models.Configuration:
    """Get config object from db."""

    strategy_configurations_to_hash = [hash(config) for config in strategy.configurations]
    if hash(configuration_id) not in strategy_configurations_to_hash:
        raise exceptions.ConfigurationNotFoundException()

    configuration = getters.find_config(configuration_id, db)
    return configuration


# def get_configuration_extra(
#         configuration: config_models.Configuration = Depends(get_configuration),
#         db: Database = Depends(get_db),
# ) -> config_models.ConfigurationExtra:
#     """Get config object from db with resolved ml model and dataset."""
#     return config_models.ConfigurationExtra(
#         **configuration.dict(by_alias=True),
#         ml_model=get_ml_model(ml_model_id=configuration.ml_model_id, db=db),
#         dataset=get_dataset(dataset_id=configuration.dataset_id, db=db),
#     )


def get_quality_requirement_id(
        quality_requirement_id: str = fastapi.Path(
            ...,
            description="The ID of the quality requirement.",
        ),
) -> PyUUID:
    """Get validated quality requirement id."""
    return transform_to_pyuuid(quality_requirement_id)


def get_quality_requirement(
        strategy: strategy_models.Strategy = Depends(get_strategy),
        quality_requirement_id: PyUUID = Depends(get_quality_requirement_id),
        db: Database = Depends(get_db),
) -> qrm.QualityRequirement:
    """Get quality requirement object form db."""
    if quality_requirement_id not in strategy.quality_requirements:
        raise exceptions.QualityRequirementNotFoundException()

    return getters.find_quality_requirement(quality_requirement_id, db=db)


def prevent_multiple_votes_with_same_prio(
        new_vote: proposal_models.PriorityVote | proposal_models.DecisionVote,
        proposal: proposal_models.Proposal = Depends(get_proposal),
        db: Database = Depends(get_db),
):
    """Check if a vote of the same priority is already present in another possible proposal."""
    all_similar_proposals = [
        proposal_models.Proposal(**g)
        for g in db[Collections.PROPOSALS].find(
            {"strategy_id": proposal.strategy_id, "content_variant": proposal.content_variant}
        )
    ]

    all_similar_proposals.remove(proposal)
    for sim_prop in all_similar_proposals:
        for vote in sim_prop.votes:
            if vote is isinstance(vote, proposal_models.PriorityVote) and (
                    vote.member == new_vote.member and vote.priority == new_vote.priority
            ):
                raise VotePriorityAlreadyExistsException()
