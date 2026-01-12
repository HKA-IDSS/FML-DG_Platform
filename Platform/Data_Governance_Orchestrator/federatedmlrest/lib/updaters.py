from pymongo.database import Database

from federatedmlrest.api.DBConnection import get_db
from federatedmlrest.api.models.common import PyUUID, Status
from federatedmlrest.lib import getters
from federatedmlrest.api.models import (dataset_models, group_models,
                                        ml_model_models, strategy_models,
                                        user_models, organisation_models)
from federatedmlrest.mongo import Collections


def update_group(old_group: group_models.Group, dict_group: dict, db: Database = get_db()):
    db[Collections.GROUPS].update_one(
        {'_governance_id': old_group.governance_id, '_current': True},
        {'$set': {"_current": False}}
    )

    db[Collections.GROUPS].insert_one(
        group_models.Group(**dict_group)
        .dict(exclude_none=True, by_alias=True)
    )


def update_organisation(old_organisation: organisation_models.Organisation, dict_organisation: dict,
                        db: Database = get_db()):
    db[Collections.ORGANISATIONS].update_one(
        {'_governance_id': old_organisation.governance_id, '_current': True},
        {'$set': {"_current": False}}
    )

    db[Collections.ORGANISATIONS].insert_one(
        organisation_models.Organisation(**dict_organisation)
        .dict(exclude_none=True, by_alias=True)
    )


def update_user(old_user: user_models.User, dict_user: dict, db: Database = get_db()):
    # dict_user = {"_governance_id": old_user.governance_id,
    #              "_version": old_user.version + 1,
    #              "_current": True,
    #              "name": new_user.name,
    #              "description": new_user.description,
    #              "organization": new_user.organisation_id,
    #              "ip": new_user.ip}

    db[Collections.USERS].update_one(
        {'_governance_id': old_user.governance_id, '_current': True},
        {'$set': {"_current": False}}
    )

    db[Collections.USERS].insert_one(
        user_models.User(**dict_user)
        .dict(exclude_none=True, by_alias=True)
    )


def update_information_strategy(old_strategy: strategy_models.Strategy, dict_strategy: dict,
                                db: Database = get_db()):
    db[Collections.STRATEGIES].update_one(
        {'_governance_id': old_strategy.governance_id, '_current': True},
        {'$set': {"_current": False}}
    )

    db[Collections.STRATEGIES].insert_one(
        strategy_models.Strategy(**dict_strategy)
        .dict(exclude_none=True, by_alias=True)
    )


def update_quality_requirements_proposals(strategy_gov_id: PyUUID, id_proposal,
                                          db: Database = get_db()):
    db[Collections.STRATEGIES].update_one(
        {'_governance_id': strategy_gov_id, '_current': True},
        {'$push': {"quality_requirements_proposals": id_proposal}}
    )


def update_configuration_proposals(strategy_gov_id: PyUUID, id_proposal, db: Database = get_db()):
    db[Collections.STRATEGIES].update_one(
        {'_governance_id': strategy_gov_id, '_current': True},
        {'$push': {"configuration_proposals": id_proposal}}
    )


def update_dataset(old_dataset: dataset_models.Dataset, dict_dataset: dict,
                   db: Database = get_db()):
    db[Collections.DATASETS].update_one(
        {'_governance_id': old_dataset.governance_id, '_current': True},
        {'$set': {"_current": False}}
    )

    db[Collections.DATASETS].insert_one(
        dataset_models.Dataset(**dict_dataset)
        .dict(exclude_none=True, by_alias=True)
    )


def update_ml_model(old_ml_model: ml_model_models.MLModel, dict_ml_model: dict,
                    db: Database = get_db()):
    db[Collections.ML_MODELS].update_one(
        {'_governance_id': old_ml_model.governance_id, '_current': True},
        {'$set': {"_current": False}}
    )

    db[Collections.ML_MODELS].insert_one(
        ml_model_models.MLModel(**dict_ml_model)
        .dict(exclude_none=True, by_alias=True)
    )


def update_accepted_proposal(proposal_id: PyUUID, db: Database = get_db()):
    db[Collections.PROPOSALS].update_one(
        {"_id": proposal_id},
        {"$set": {"status": "ACCEPTED"}}
    )

def update_rejected_proposal(proposal_id: PyUUID, db: Database = get_db()):
    db[Collections.PROPOSALS].update_one(
        {"_id": proposal_id},
        {"$set": {"status": "REJECTED"}}
    )

def update_obsolete_proposal(proposal_id: PyUUID, db: Database = get_db()):
    db[Collections.PROPOSALS].update_one(
        {"_id": proposal_id},
        {"$set": {"status": "OBSOLETE"}}
    )
