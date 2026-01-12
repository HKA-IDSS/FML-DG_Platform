from uuid import UUID

from pymongo.database import Database

from federatedmlrest.api import exceptions
from federatedmlrest.api.DBConnection import get_db
from federatedmlrest.api.models import (dataset_models, group_models,
                                        ml_model_models, proposal_models,
                                        strategy_models, organisation_models, user_models)
from federatedmlrest.api.models.common import MongoID, PyUUID
from federatedmlrest.lib import getters
from federatedmlrest.mongo import Collections


def delete_group(group_governance_id: PyUUID, db = get_db()) -> None:
    """Delete a group."""
    db[Collections.GROUPS].update_many(
        {"_governance_id": group_governance_id},
        {"$set": {"_deleted": True}}
    )

    # for strategy_governance_id in group.strategies:
    #     strategy = getters.find_strategy_governance(strategy_governance_id)
    #     delete_strategy(strategy)


def delete_config(config_id: PyUUID, db = get_db()) -> None:
    """Delete a config."""
    db[Collections.CONFIGURATIONS].update_one(
        MongoID.id_to_mongo_query(config_id),
        {'$set': {"_deleted": True}}
    )


def delete_quality_requirement(quality_requirement_id: PyUUID, db = get_db()) -> None:
    """Delete a quality requirement."""
    db[Collections.QUALITY_REQUIREMENTS].update_one(
        MongoID.id_to_mongo_query(quality_requirement_id),
        {'$set': {"_deleted": True}}
    )


def delete_strategy(strategy_governance_id: PyUUID, db = get_db()) -> None:
    """Delete a strategy."""

    # for config_id in strategy.configurations:
    #     delete_config(config_id)

    db[Collections.STRATEGIES].update_many(
        {"_governance_id": strategy_governance_id},
        {'$set': {"_deleted": True}}
    )


def delete_ml_model(ml_model_governance_id: PyUUID, db = get_db()) -> None:
    """Delete the ml model."""
    db[Collections.ML_MODELS].update_many(
        {"_governance_id": ml_model_governance_id},
        {'$set': {"_deleted": True}}
    )


def delete_dataset(dataset_governance_id: PyUUID, db = get_db()) -> None:
    """Delete the dataset."""
    db[Collections.DATASETS].update_many(
        {"_governance_id": dataset_governance_id},
        {'$set': {"_deleted": True}}
    )


def delete_proposal(proposal_id: PyUUID, db = get_db()) -> None:
    """Delete the proposal. This operation cannot be undone."""
    db[Collections.PROPOSALS].delete_one(MongoID.id_to_mongo_query(proposal_id))


def delete_user(user_governance_id: PyUUID, db = get_db()) -> None:
    """Delete a user."""
    db[Collections.USERS].update_many(
        {"_governance_id": user_governance_id},
        {'$set': {"_deleted": True}}
    )


def delete_organisation(organisation_governance_id: PyUUID, db = get_db()) -> None:
    """Delete an organisation."""
    db[Collections.ORGANISATIONS].update_many(
        {"_governance_id": organisation_governance_id},
        {'$set': {"_deleted": True}}
    )
