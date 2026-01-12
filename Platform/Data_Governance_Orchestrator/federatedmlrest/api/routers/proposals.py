import asyncio
import functools
from typing import List, Union
from uuid import UUID

import fastapi
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status as http_codes
from pymongo.database import Database
from starlette.responses import Response

from federatedmlrest.api import dependencies, exceptions
from federatedmlrest.api.DBConnection import get_db
from federatedmlrest.api.models import (
    proposal_models, strategy_models, quality_requirements_models, config_models,
)
from federatedmlrest.api.models.common import PyUUID, Status, WithStatus
from federatedmlrest.api.models.proposal_models import (
    ProposalContent,
    ProposalOperation,
    Proposal,
    PriorityVote,
    DecisionVote, AcceptanceTally,
)
from federatedmlrest.api.tags import Tags
from federatedmlrest.keycloak_auth import get_current_user, require_user_in_group
from federatedmlrest.lib import deleters, getters, updaters, validators
from federatedmlrest.mongo import Collections, MongoDB
from federatedmlrest.yaml_generator import createYaml

router = APIRouter(prefix="/proposals", tags=[Tags.PROPOSALS])

@router.get(
    "",
    responses={
        http_codes.HTTP_200_OK: {"description": "Returns a list with all proposals."}
    },
    response_model=List[proposal_models.Proposal],
    response_model_exclude_none=True,
)
def get_all_proposals(
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user),
) -> List[proposal_models.Proposal]:
    """Get all proposals."""
    return [
        proposal_models.Proposal(**g) for g in db[Collections.PROPOSALS].find()
    ]

@router.get(
    "/strategies/{strategy_governance_id}",
    responses={
        http_codes.HTTP_200_OK: {"description": "Returns a list with all proposals."}
    },
    response_model=List[proposal_models.Proposal],
    response_model_exclude_none=True,
)
def get_all_proposals_from_strategies(
    strategy_governance_id: PyUUID,
    db: Database = Depends(get_db),
    token: dict = Depends(get_current_user),
) -> List[proposal_models.Proposal]:
    """Get all proposals."""
    strategy = getters.find_strategy_governance(strategy_governance_id)
    group = getters.find_group_governance(strategy.belonging_group)
    get_user_in_group(str(group.id))
    quality_req_proposals = MongoDB.resolve_id_list(
        db,
        Collections.PROPOSALS,
        strategy.quality_requirements_proposals,
    )

    config_proposals = MongoDB.resolve_id_list(
        db,
        Collections.PROPOSALS,
        strategy.configuration_proposals,
    )
    proposals = quality_req_proposals + config_proposals

    return [
        proposal_models.Proposal(**proposal) for proposal in proposals
    ]

@router.get(
    "/{proposal_id}",
    responses={
        http_codes.HTTP_200_OK: {"description": "Returns a list with all proposals."}
    },
    response_model=proposal_models.Proposal,
    response_model_exclude_none=True,
)
def get_proposal(
        proposal_id: PyUUID,
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user)
) -> proposal_models.Proposal:
    """Get all proposals."""
    return getters.find_proposal(proposal_id)

@router.post(
    '/quality_requirements',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'The quality requirement was created. Returns the new quality requirement.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'A resource could not be found (Group or Strategy).',
        },
    },
    response_model=proposal_models.Proposal,
    response_model_exclude_none=True,
)
def add_quality_requirement_proposal(
        new_quality_requirement_proposal: proposal_models.AddProposal,
        # strategy: strategy_models.Strategy = Depends(dependencies.get_strategy),
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user),
) -> proposal_models.Proposal:
    """Add a new quality requirement."""
    new_proposal_dict: dict = \
        proposal_models.Proposal(**new_quality_requirement_proposal.dict()).dict(exclude_none=True, by_alias=True)
    strategy = getters.find_strategy_governance(new_proposal_dict["strategy_id"], db=db)

    if new_quality_requirement_proposal.operation_variant == proposal_models.ProposalOperation.CREATE:
        # It cannot exist another quality requirement in active with the same metric that is being created.
        validators.check_existing_same_type_quality_requirement(
            strategy.quality_requirements,
            new_proposal_dict["proposal_content"]["quality_requirement"]["quality_req_type"],
            new_proposal_dict["proposal_content"]["quality_requirement"]["metric"]
        )
    else:
        validators.check_existing_referenced_quality_requirement(
            new_quality_requirement_proposal.referenced_content,
            strategy.quality_requirements
        )
    new_proposal_dict["proposer"] = token["sub"]
    db[Collections.PROPOSALS].insert_one(new_proposal_dict)
    updaters.update_quality_requirements_proposals(new_proposal_dict["strategy_id"], new_proposal_dict["_id"], db)

    return proposal_models.Proposal(**new_proposal_dict)


@router.post(
    '/configurations',
    responses={
        http_codes.HTTP_200_OK: {
            'description': 'The quality requirement was created. Returns the new quality requirement.',
        },
        http_codes.HTTP_404_NOT_FOUND: {
            'description': 'A resource could not be found (Group or Strategy).',
        },
    },
    response_model=proposal_models.Proposal,
    response_model_exclude_none=True,
)
def add_configuration_proposal(
        new_configuration_proposal: proposal_models.AddProposal,
        # strategy: strategy_models.Strategy = Depends(dependencies.get_strategy),
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user),
) -> proposal_models.Proposal:
    """Add a new configuration proposal."""
    validators.object_with_version_exists(
        db[Collections.ML_MODELS],
        new_configuration_proposal.proposal_content.ml_model_id,
        new_configuration_proposal.proposal_content.ml_model_version,
        exceptions.MLModelNotFoundException(),
    )
    validators.object_with_version_exists(
        db[Collections.DATASETS],
        new_configuration_proposal.proposal_content.dataset_id,
        new_configuration_proposal.proposal_content.dataset_version,
        exceptions.DatasetNotFoundException(),
    )

    new_proposal_dict = proposal_models.Proposal(**new_configuration_proposal.dict()).dict(
        exclude_none=True, by_alias=True
    )
    getters.find_strategy_governance(new_proposal_dict["strategy_id"], db=db)
    new_proposal_dict["proposer"] = token["sub"]
    db[Collections.PROPOSALS].insert_one(new_proposal_dict)
    updaters.update_configuration_proposals(new_proposal_dict["strategy_id"], new_proposal_dict["_id"], db)

    return proposal_models.Proposal(**new_proposal_dict)


@router.delete(
    "/{proposal_id}",
    status_code=http_codes.HTTP_204_NO_CONTENT,
    responses={
        http_codes.HTTP_204_NO_CONTENT: {
            "description": "You have successfully deleted your Proposal.",
        },
        http_codes.HTTP_404_NOT_FOUND: {"description": "The proposal doesnt exist."},
    },
    response_model_exclude_none=True,
)
def delete_proposal(
        proposal: PyUUID = Depends(dependencies.get_proposal),
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user),
) -> Response:
    """Delete the Proposal."""
    deleters.delete_proposal(proposal, db)
    return Response(status_code=http_codes.HTTP_204_NO_CONTENT)


def get_user_in_group(group_id: str, admin_allowed: bool = False):
    return require_user_in_group(group_id, admin_allowed)


@router.post(
    "/{proposal_id}/votes",
    responses={
        http_codes.HTTP_200_OK: {
            "description": "You have successfully voted.",
        },
        http_codes.HTTP_404_NOT_FOUND: {"description": "A resource doesnt exist."},
        http_codes.HTTP_409_CONFLICT: {
            "description": "Vote with same priority exists elsewhere."
        },
    },
    response_model=Proposal,
    response_model_exclude_none=True,
    dependencies=[Depends(dependencies.prevent_multiple_votes_with_same_prio)],
)
def add_vote(
        new_vote: Union[PriorityVote, DecisionVote],
        proposal: Proposal = Depends(dependencies.get_proposal),
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user),
) -> proposal_models.Proposal:
    """Create a new vote."""
    group = dependencies.get_group(group_governance_id=proposal.group, db=db)
    if new_vote.member not in group.members:
        raise HTTPException(status_code=403, detail="User not in group")
    member = dependencies.get_user(user_governance_id=new_vote.member, db=db)

    if member.governance_id not in [vote.member for vote in proposal.votes]:
        proposal.votes.append(new_vote)
    else:
        for vote in proposal.votes:
            if vote.member == member.governance_id:
                if isinstance(new_vote, PriorityVote):
                    vote.priority = new_vote.priority
                else:
                    vote.decision = new_vote.decision

    db[Collections.PROPOSALS].update_one(
        proposal.mongo_query(), {"$set": proposal.dict(by_alias=True)}
    )

    return getters.find_proposal(proposal_id=proposal.id, db=db)


@router.delete(
    "/{proposal_id}/votes/{member_id}",
    status_code=http_codes.HTTP_204_NO_CONTENT,
    responses={
        http_codes.HTTP_204_NO_CONTENT: {
            "description": "You have successfully deleted your vote.",
        },
        http_codes.HTTP_404_NOT_FOUND: {"description": "The proposal doesnt exist."},
    },
    response_model_exclude_none=True,
)
def delete_vote(
        user_id: PyUUID = Depends(dependencies.get_user_governance_id),
        proposal: proposal_models.Proposal = Depends(dependencies.get_proposal),
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user),
) -> Response:
    """Delete the Vote."""
    updated_votes = [vote for vote in proposal.votes if vote.member != user_id]
    proposal.votes = updated_votes
    db[Collections.PROPOSALS].update_one(
        proposal.mongo_query(), {"$set": proposal.dict(by_alias=True)}
    )

    return Response(status_code=http_codes.HTTP_204_NO_CONTENT)


@router.post(
    "/{strategy_governance_id}/count_votes_configuration_proposals",
    responses={
        http_codes.HTTP_200_OK: {
            "description": "Successfully counted votes and processed configuration proposals."
        },
        http_codes.HTTP_404_NOT_FOUND: {"description": "A resource doesnt exist."},
        http_codes.HTTP_409_CONFLICT: {"description": "Votes have already been counted."},
    },
    response_model=Union[proposal_models.VoteTally, proposal_models.TieTally],
    response_model_exclude_none=True,
)
def count_votes_configuration_proposals(
    strategy: strategy_models.Strategy = Depends(dependencies.get_strategy),
    # proposal_type: proposal_models.ProposalType = fastapi.Query(...),
    db: Database = Depends(get_db),
    token: dict = Depends(get_current_user),
) -> proposal_models.VoteTally:
    """Count votes and process configuration proposals."""
    # Check if configuration_proposals is empty (already processed)
    if not strategy.configuration_proposals:
        raise HTTPException(
            status_code=http_codes.HTTP_409_CONFLICT,
            detail="Configuration proposals have already been processed for this strategy."
        )
    
    group = dependencies.get_group(group_governance_id=strategy.belonging_group, db=db)
    priorities = [1, 2, 3]

    # elif proposal_type == ProposalType.CONFIGURATION:
    configuration_proposals = [
        getters.find_proposal(proposal_id, db)
        for proposal_id in strategy.configuration_proposals
    ]
    
    # Check if any proposals have already been processed
    for proposal in configuration_proposals:
        if proposal.status in [Status.ACCEPTED, Status.REJECTED]:
            raise HTTPException(
                status_code=http_codes.HTTP_409_CONFLICT,
                detail=f"Proposal {proposal.id} has already been processed with status: {proposal.status}"
            )

    # collection = Collections.CONFIGURATIONS
    winner, vote_tally = handle_configurations(
        configuration_proposals, len(group.members), priorities
    )
    if winner is None:  # A tie happened
        return proposal_models.TieTally(
            winner=None, votes=vote_tally, member_count=len(group.members)
        )
    else: # No tie happened
        new_strategy_dict = strategy.dict(exclude_none=True, by_alias=True)
        sole_winner: PyUUID = winner
        rejected_configuration_proposals = [rejected_proposal
                                            for rejected_proposal
                                            in configuration_proposals
                                            if rejected_proposal.id != sole_winner]
        updaters.update_accepted_proposal(sole_winner, db)
        for rejected_proposal in rejected_configuration_proposals:
            updaters.update_rejected_proposal(rejected_proposal.id, db)
        new_configuration = getters.find_proposal(sole_winner, db)
        new_configuration_dict = (config_models.Configuration(**new_configuration.proposal_content.dict())
                                  .dict(exclude_none=True, by_alias=True))
        new_configuration_dict["strategy_linked"] = new_strategy_dict["_governance_id"]
        db[Collections.CONFIGURATIONS].insert_one(new_configuration_dict)
        inserted_config: config_models.Configuration = getters.find_config(new_configuration_dict["_id"], db)
        new_strategy_dict.pop("_id")
        new_strategy_dict["_version"] += 1
        new_strategy_dict["configurations"].append(inserted_config.id)
        new_strategy_dict["configuration_proposals"] = list()
        updaters.update_information_strategy(strategy, new_strategy_dict, db)
        newly_created_strategy = getters.find_strategy_governance(new_strategy_dict["_governance_id"], db=db)
        asyncio.run(createYaml(newly_created_strategy, inserted_config.id, db))
        return proposal_models.VoteTally(
            winner=winner, votes=vote_tally, member_count=len(group.members),
            created_configuration_id=inserted_config.id,
            created_configuration_model_id=inserted_config.ml_model_id,
            created_configuration_dataset_id=inserted_config.dataset_id,
            created_configuration_group_id=strategy.belonging_group
        )



@router.post(
    "/{strategy_governance_id}/count_votes_qr/{proposal_id}",
    responses={
        http_codes.HTTP_200_OK: {
            "description": "Successfully counted votes and processed quality requirement proposal."
        },
        http_codes.HTTP_404_NOT_FOUND: {"description": "A resource doesnt exist."},
        http_codes.HTTP_409_CONFLICT: {"description": "Votes have already been counted."},
    },
    response_model=proposal_models.AcceptanceTally,
    response_model_exclude_none=True,
)
def count_votes_quality_requirements(
        strategy: strategy_models.Strategy = Depends(dependencies.get_strategy),
        qr_proposal: proposal_models.Proposal = Depends(dependencies.get_proposal),
        db: Database = Depends(get_db),
        token: dict = Depends(get_current_user),
) -> proposal_models.AcceptanceTally:
    """Count votes and process quality requirement proposals."""
    # Check if proposal has already been processed
    if qr_proposal.status in [Status.ACCEPTED, Status.REJECTED]:
        raise HTTPException(
            status_code=http_codes.HTTP_409_CONFLICT,
            detail=f"This proposal has already been processed with status: {qr_proposal.status}"
        )
    
    votes, accepted = handle_quality_requirements(qr_proposal)
    new_strategy_dict = strategy.copy().dict(exclude_none=True, by_alias=True)
    new_strategy_dict["quality_requirements_proposals"].remove(qr_proposal.id)
    created_qr_id = None
    if accepted:
        if qr_proposal.operation_variant == proposal_models.ProposalOperation.DELETE: ## Only DELETE
            new_strategy_dict["quality_requirements"].remove(qr_proposal.referenced_content)
        else:
            new_qr_dict: dict = (
                quality_requirements_models.QualityRequirement(**qr_proposal.proposal_content.dict())
                .dict(exclude_none=True, by_alias=True)
            )
            if qr_proposal.operation_variant == proposal_models.ProposalOperation.UPDATE: ## Only UPDATE
                new_strategy_dict["quality_requirements"].remove(qr_proposal.referenced_content)

            ## UPDATE and CREATE
            created_qr_id = new_qr_dict["_id"]  # Capture the created QR ID
            new_strategy_dict["quality_requirements"].append(created_qr_id)
            db[Collections.QUALITY_REQUIREMENTS].insert_one(new_qr_dict)

        ## Common to all operations
        new_strategy_dict["_version"] += 1
        new_strategy_dict.pop("_id")
        updaters.update_accepted_proposal(qr_proposal.id, db)
        updaters.update_information_strategy(old_strategy=strategy, dict_strategy=new_strategy_dict, db=db)
    else:
        quality_requirement_proposals_list = strategy.quality_requirements_proposals
        quality_requirement_proposals_list.remove(qr_proposal.id)
        updaters.update_rejected_proposal(qr_proposal.id, db)
        db[Collections.STRATEGIES].update_one(
            {"_id": strategy.id},
            {"$set": {"quality_requirements_proposals": quality_requirement_proposals_list}}
        )

    return AcceptanceTally(
        proposal=qr_proposal.id,
        accepted=accepted,
        votes=votes,
        member_count=len(votes),
        created_quality_requirement_id=created_qr_id
    )

def split_by_priority(
        strategy_proposal: Proposal, priorities: list[int] = [1, 2, 3]
) -> dict:
    """
    Split proposed vote by priority.
    :param strategy_proposal: A strategy proposal.
    :param priorities: List of priorities.
    :return: Proposal dict with split up priorities.
    """
    vote_tally = {}
    vote_tally[strategy_proposal.id] = {
        f"priority_{priority}": [
            vote for vote in strategy_proposal.votes if vote.priority == priority
        ]
        for priority in priorities
    }
    return vote_tally


def count_priorities(proposal: dict, priority: int) -> int:
    count = 0
    for p in range(1, priority + 1):
        count += len(proposal[f"priority_{p}"])
    return count


def choose_winner(
        vote_tally: dict, majority_required: float, priorities: list[int] = [1, 2, 3]
):
    winning_vote_count = 0
    winner = None
    for prio in priorities:
        for vote_tally_id, priorities in vote_tally.items():
            vote_count = count_priorities(priorities, prio)
            if vote_count > majority_required:
                if winner and vote_count > winning_vote_count:
                    winner = vote_tally_id
                    winning_vote_count = vote_count
                elif not winner:
                    winner = vote_tally_id
                    winning_vote_count = vote_count
                elif vote_count == winning_vote_count:
                    winner = None
        if winner:
            break
        winning_vote_count = 0
    return winner


def handle_quality_requirements(qr_proposal):
    votes = qr_proposal.votes
    yes_votes = sum([1 for vote in votes if vote.decision])
    accepted = yes_votes > (len(votes) / 2)
    votes = {decisionVote.member: decisionVote.decision for decisionVote in votes}
    return votes, accepted


def handle_configurations(
        strategy_proposals, group_members: int, priorities: list[int] = [1, 2, 3]
):
    vote_tally = dict()
    for proposal in strategy_proposals:
        vote_tally.update(split_by_priority(proposal, priorities))
    majority_required = group_members / 2
    winner = choose_winner(vote_tally, majority_required, priorities)
    if winner is None:
        return None, vote_tally
    else:
        return winner, vote_tally


def handle_policies(strategy_proposals):
    raise NotImplementedError()


def handle_information_update(strategy_proposals):
    raise NotImplementedError()


# def remove_from_strategy(db, collection, winner, variants, strategy):
#     for variant in variants:
#         if variant.id not in winner and variant.status is Status.REJECTED:
#             if collection is Collections.QUALITY_REQUIREMENTS:
#                 strategy.quality_requirements.remove(variant.id)
#                 db[Collections.STRATEGIES].update_one(
#                     strategy.mongo_query(),
#                     {'$set': {'quality_requirements': strategy.quality_requirements}},
#                 )
#
#             if collection is Collections.CONFIGURATIONS:
#                 strategy.configurations.remove(variant.id)
#                 db[Collections.STRATEGIES].update_one(
#                     strategy.mongo_query(),
#                     {'$set': {'configurations': strategy.configurations}},
#                 )


def delete_variants(db, deleter, winner, variants):
    to_delete = []
    for variant in variants:
        if variant.status is Status.ACCEPTED:
            variant.status = Status.OBSOLETE
        elif variant.status is Status.REJECTED:
            to_delete.append(variant.id)
        else:
            variant.status = Status.REJECTED
        if variant.id in winner:
            variant.status = Status.ACCEPTED

        db[Collections.PROPOSALS].update_one(
            variant.mongo_query(), {"$set": variant.dict(by_alias=True)}
        )

    for delete in to_delete:
        deleter(delete)


def delete_proposals(db, configuration_proposals):
    for proposal in configuration_proposals:
        deleters.delete_proposal(db=db, proposal=proposal)
