from typing import List
from uuid import UUID
from pymongo.database import Database

from federatedmlrest.api import exceptions
from federatedmlrest.api.DBConnection import get_db
from federatedmlrest.api.models import (config_models, dataset_models,
                                        group_models, ml_model_models,
                                        proposal_models, quality_requirements_models,
                                        strategy_models, user_models, organisation_models, result_models)
from federatedmlrest.api.models.common import MongoID, PyUUID, MongoIDAndVersion
from federatedmlrest.mongo import Collections


# def find_member(member_id: UUID, db: Database) -> member_models.Member:
#     """Find member in db."""
#     member = db[Collections.MEMBERS].find_one(
#         MongoID.id_to_mongo_query(member_id),
#     )
#
#     if not member:
#         raise exceptions.MemberNotFoundException()
#
#     return member_models.Member(**member)



def find_group_governance(group_governance_id: PyUUID, version=-1, db: Database = get_db()) -> group_models.Group:
    """Find group in db."""
    if version == -1:
        group = db[Collections.GROUPS].find_one(
            MongoIDAndVersion.get_current_document(group_governance_id)
        )
    else:
        group = db[Collections.GROUPS].find_one(
            MongoIDAndVersion.get_version_document(group_governance_id, version),
        )

    if group is None:
        raise exceptions.GroupNotFoundException()

    return group_models.Group(**group)


def find_user_governance(governance_user_id: PyUUID, version=-1, db: Database = get_db()) -> user_models.User:
    """Find member in db."""
    if version == -1:
        user = db[Collections.USERS].find_one(
            MongoIDAndVersion.get_current_document(governance_user_id)
        )

    else:
        user = db[Collections.USERS].find_one(
            MongoIDAndVersion.get_version_document(governance_user_id, version)
        )
    if not user:
        raise exceptions.UserNotFoundException()

    return user_models.User(**user)


# def find_user(user_id: PyUUID, db: Database) -> user_models.User:
#     """Find member in db."""
#     user = db[Collections.USERS].find_one(
#         MongoID.id_to_mongo_query(user_id),
#     )
#
#     if not user:
#         raise exceptions.UserNotFoundException()
#
#     return user_models.User(**user)

# def find_group(group_id: UUID, db: Database):
#     group = db[Collections.GROUPS].find_one(MongoID.id_to_mongo_query(group_id)
#
#     if not group:
#         raise exceptions.GroupNotFoundException()
#
#     return group_models.Group(**group)


def find_config(config_id: UUID, db: Database = get_db()) -> config_models.Configuration:
    """Find config in db."""
    config = db[Collections.CONFIGURATIONS].find_one(
        MongoID.id_to_mongo_query(config_id),
    )

    if not config:
        raise exceptions.ConfigurationNotFoundException()

    return config_models.Configuration(**config)


def find_strategy_governance(strategy_governance_id: UUID, version=-1, db: Database = get_db()) \
        -> strategy_models.Strategy:
    """Find strategy in db."""
    if version == -1:
        strat = db[Collections.STRATEGIES].find_one(
            MongoIDAndVersion.get_current_document(strategy_governance_id)
        )

    else:
        strat = db[Collections.STRATEGIES].find_one(
            MongoIDAndVersion.get_version_document(strategy_governance_id, version)
        )
    if not strat or strat is None:
        raise exceptions.StrategyNotFoundException()

    return strategy_models.Strategy(**strat)


# def find_strategy(_id: UUID, db: Database) \
#         -> strategy_models.Strategy:
#     """Find strategy in db."""
#     strat = db[Collections.STRATEGIES].find_one(
#         {"_id": _id}
#     )
#
#     if not strat:
#         raise exceptions.StrategyNotFoundException()
#
#     return strategy_models.Strategy(**strat)


def find_quality_requirement(qr_id: UUID, db: Database = get_db()) -> quality_requirements_models.QualityRequirement:
    """Find quality requirement in db."""
    qr = db[Collections.QUALITY_REQUIREMENTS].find_one(
        MongoID.id_to_mongo_query(qr_id),
    )

    if not qr:
        raise exceptions.QualityRequirementNotFoundException()

    return quality_requirements_models.QualityRequirement(**qr)


# def find_dataset(dataset_id: PyUUID, db: Database) -> dataset_models.Dataset:
#     """Find dataset in db."""
#     dataset = db[Collections.DATASETS].find_one(
#         MongoID.id_to_mongo_query(dataset_id),
#     )
#
#     if not dataset:
#         raise exceptions.DatasetNotFoundException()
#
#     return dataset_models.Dataset(**dataset)


def find_dataset_governance(dataset_governance_id: PyUUID, version=-1, db: Database = get_db()) -> dataset_models.Dataset:
    """Find dataset in db."""
    if version == -1:
        dataset = db[Collections.DATASETS].find_one(
            MongoIDAndVersion.get_current_document(dataset_governance_id),
        )
    else:
        dataset = db[Collections.DATASETS].find_one(
            MongoIDAndVersion.get_version_document(dataset_governance_id, version),
        )

    if not dataset:
        raise exceptions.DatasetNotFoundException()

    return dataset_models.Dataset(**dataset)
#
# def find_ml_model(ml_model_id: PyUUID, db: Database) -> ml_model_models.MLModel:
#     """Find ml model in db."""
#     ml_model = db[Collections.ML_MODELS].find_one(
#         MongoID.id_to_mongo_query(ml_model_id),
#     )
#
#     if not ml_model:
#         raise exceptions.MLModelNotFoundException()
#
#     return ml_model_models.MLModel(**ml_model)


def find_ml_model_governance(ml_model_governance_id: PyUUID, version=-1, db: Database = get_db()):
    """Find ml model in db."""
    if version == -1:
        ml_model = db[Collections.ML_MODELS].find_one(
            MongoIDAndVersion.get_current_document(ml_model_governance_id)
        )

    else:
        ml_model = db[Collections.ML_MODELS].find_one(
            MongoIDAndVersion.get_version_document(ml_model_governance_id, version)
        )

    if not ml_model:
        raise exceptions.MLModelNotFoundException()

    return ml_model_models.MLModel(**ml_model)


def find_proposal(proposal_id: PyUUID, db: Database = get_db()) -> proposal_models.Proposal:
    """Find proposal in db."""

    proposal = db[Collections.PROPOSALS].find_one(
        MongoID.id_to_mongo_query(proposal_id),
    )

    if not proposal:
        raise exceptions.ProposalNotFoundException()

    return proposal_models.Proposal(**proposal)




def find_organisation_governance(organisation_governance_id: PyUUID, version=-1,
                                 db: Database = get_db()) \
        -> organisation_models.Organisation:
    """Find member in db."""
    if version == -1:
        organisation = db[Collections.ORGANISATIONS].find_one(
            MongoIDAndVersion.get_current_document(organisation_governance_id),
        )
    else:
        organisation = db[Collections.ORGANISATIONS].find_one(
            MongoIDAndVersion.get_version_document(organisation_governance_id, version),
        )

    if not organisation:
        raise exceptions.OrganisationNotFoundException()

    return organisation_models.Organisation(**organisation)


def find_results_training_information_governance(configuration_id: PyUUID, db: Database = get_db()) \
        -> result_models.TrainingConfigurationInformation:
    """Find member in db."""
    training_configuration_information = db[Collections.RESULTS].find_one(
        {"configuration_id": configuration_id},
    )

    if not training_configuration_information:
        raise exceptions.TrainingConfigurationNotFoundException()

    return result_models.TrainingConfigurationInformation(**training_configuration_information)


""" More specific queries """

def return_all_correctness_proposals(proposal_ids: List[PyUUID], db: Database = get_db()):
    list_of_ids = [MongoID.id_to_mongo_query(proposal_id) for proposal_id in proposal_ids]

    proposals = db[Collections.PROPOSALS].find({
        "$in": list_of_ids, "quality_req_type": "Correctness"
    })