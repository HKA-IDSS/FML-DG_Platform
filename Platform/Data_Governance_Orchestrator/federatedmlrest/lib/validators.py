from typing import List

from pymongo.collection import Collection
from pymongo.database import Database

from federatedmlrest.api import exceptions, errors
from federatedmlrest.api.DBConnection import get_db
from federatedmlrest.api.models import (config_models, dataset_models,
                                        ml_model_models, quality_requirements_models)
from federatedmlrest.api.models.common import MongoID, PyUUID, MongoIDAndVersion
from federatedmlrest.lib import getters
from federatedmlrest.mongo import Collections


def object_exists(
    collection: Collection,
    object_id: PyUUID,
    should_raise: exceptions.HTTPNotFoundException,
) -> None:
    """Check that object exists in DB."""
    if not collection.find_one(MongoID.id_to_mongo_query(object_id)):
        raise should_raise


def object_with_version_exists(
    collection: Collection,
    object_id: PyUUID,
    version: int,
    should_raise: exceptions.HTTPNotFoundException,
) -> None:
    """Check that object exists in DB."""
    if not collection.find_one(MongoIDAndVersion.get_version_document(object_id, version)):
        raise should_raise


def check_for_ml_model_references(
    db: Database,
    ml_model: ml_model_models.MLModel,
) -> None:
    """Check that ml model is not referenced in any configuration."""
    for config in (config_models.Configuration(**c) for c in db[Collections.CONFIGURATIONS].find()):
        if config.ml_model_id == ml_model.governance_id:
            raise exceptions.MLModelConflictException()


def check_for_dataset_references(
    db: Database,
    dataset: dataset_models.Dataset,
) -> None:
    """Check that dataset is not referenced in any configuration."""
    for config in (config_models.Configuration(**c) for c in db[Collections.CONFIGURATIONS].find()):
        if config.dataset_id == dataset.governance_id:
            raise exceptions.DatasetConflictException()


def check_existing_same_type_quality_requirement(proposals_ids: List[PyUUID],
                                                 qr_type: str,
                                                 qr_specific_metric: quality_requirements_models.CorrectnessMethods):
    db = get_db()
    number_of_existing_quality_req = db[Collections.QUALITY_REQUIREMENTS].count_documents({"_id": {"$in": proposals_ids},
                                               "quality_requirement.quality_req_type": qr_type,
                                               "quality_requirement.metric": qr_specific_metric})
    if number_of_existing_quality_req > 0:
        raise exceptions.ExistingQualityRequirement()


def check_existing_referenced_quality_requirement(searched_qr: PyUUID, list_qr_strategy: List[PyUUID]):
    try: getters.find_quality_requirement(searched_qr)
    except exceptions.ProposalNotFoundException(): raise exceptions.ProposalNotFoundException()

    if searched_qr not in list_qr_strategy:
        raise exceptions.ProposalNotFoundException()


#TODO: Create validator for policy.
# def check_existing_referenced_policy(searched_policy: PyUUID):
#     try: getters.find_policy(searched_policy)
#     except exceptions.ProposalNotFoundException(): raise exceptions.ProposalNotFoundException()