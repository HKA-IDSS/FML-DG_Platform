import os
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional

import pymongo
import yaml
from bson import UuidRepresentation, ObjectId
from pymongo import MongoClient
from pymongo.database import Database

from federatedmlrest.api.models.common import PyUUID


class Collections(str, Enum):
    """MongoDB's collections for different types."""

    GROUPS: str = 'groups'
    CONFIGURATIONS: str = 'configurations'
    STRATEGIES: str = 'strategies'
    # MEMBERS: str = 'members'
    ML_MODELS: str = 'mlmodels'
    DATASETS: str = 'datasets'
    HYPERPARAMETER: str = 'hyperparameter'
    PROPOSALS: str = 'proposals'
    QUALITY_REQUIREMENTS: str = 'quality_requirements'
    USERS: str = 'users'
    ORGANISATIONS: str = 'organisations'
    RESULTS: str = 'results'


class MongoDB:
    """The MongoDB class."""

    def __init__(self, path=None, timeout_ms: Optional[int] = None):
        if path:
            config_path = path
        else:
            config_path = Path(os.path.dirname(__file__)) / 'config.yml'

        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
            url = config["dbconfig"]["dburl"]
            port = config["dbconfig"]["port"]
            collection = config["dbconfig"]["collection"]
            # username = config["dbconfig"]["username"]
            # password = config["dbconfig"]["password"]

        self.db = getattr(
            MongoClient(url + port,
                        timeoutMS=timeout_ms,
                        uuidRepresentation='standard'),
            collection)

        self.db[Collections.ORGANISATIONS].create_index(["governance_id", ("version", pymongo.DESCENDING)])
        self.db[Collections.GROUPS].create_index(["governance_id", ("version", pymongo.DESCENDING)])
        self.db[Collections.USERS].create_index(["governance_id", ("version", pymongo.DESCENDING)])
        self.db[Collections.STRATEGIES].create_index(["governance_id", ("version", pymongo.DESCENDING)])
        self.db[Collections.ML_MODELS].create_index(["governance_id", ("version", pymongo.DESCENDING)])
        self.db[Collections.DATASETS].create_index(["governance_id", ("version", pymongo.DESCENDING)])
        self.db[Collections.CONFIGURATIONS].create_index(["governance_id", ("version", pymongo.DESCENDING)])
        self.db[Collections.RESULTS].create_index(["training_configuration_id"])
        # self.db[Collections.QUALITY_REQUIREMENTS].create_index(["strategy_type",
        #                                                         "quality_requirement.quality_req_type"])

    @staticmethod
    def db_obj_format(db_obj):
        """
        This function formats objects stored in the database
        depending on the given type to human-readable formats

        Args:
            db_obj: The object to format (list, dict, pymongo cursor, pymongo object id)

        Returns:
            The formatted object (a list, dict, string, or the original type)

        """
        if type(db_obj) is list:
            formatted_list = []
            for sub_obj in db_obj:
                formatted_list.append(MongoDB.db_obj_format(sub_obj))
            return formatted_list

        elif type(db_obj) is dict:
            if '_id' in db_obj:
                db_obj['_id'] = str(db_obj['_id'])
            for attribute in db_obj:
                if type(db_obj[attribute]) is dict or type(
                        db_obj[attribute]) is list:
                    db_obj[attribute] = MongoDB.db_obj_format(
                        db_obj[attribute])
            return db_obj

        elif type(db_obj) is pymongo.cursor.Cursor:
            formatted_list = []
            for sub_obj in list(db_obj):
                formatted_list.append(MongoDB.db_obj_format(sub_obj))
            return formatted_list

        elif type(db_obj) is ObjectId:
            return str(db_obj)

        else:
            return db_obj

    @staticmethod
    def resolve_governance_id_list(db: Database, resource_collection: Collections, ids: List[PyUUID]) -> List[
        Any]:
        """
        Read all objects for a given list of IDs from the database.

        Args:
            db: The database to read
            resource_collection: Resource collection = corresponding collection in Mongo DB
            ids: List of id's of entities of the resource type

        Return:
            A list with objects of the resource type

        """
        resolved_list = []
        for _id in ids:
            obj = db[resource_collection].find_one({"_governance_id": _id, "_current": True, "_deleted": False})
            if obj:
                resolved_list.append(obj)
        return resolved_list

    @staticmethod
    def resolve_id_list(db, resource_type, ids: list):
        """
        Reads for a given list of IDs each object from the database

        Args:
            db: The database to read
            resource_type: Resource type = corresponding collection in Mongo DB
            ids: List of id's of entities of the resource type

        Returns:
            A list with objects of the resource type

        """
        resolved_list = []
        for id in ids:
            # obj = db[resource_type].find_one({"_id": ObjectId(id)})
            obj = db[resource_type].find_one({"_id": id})
            if obj:
                resolved_list.append(obj)
        return resolved_list
