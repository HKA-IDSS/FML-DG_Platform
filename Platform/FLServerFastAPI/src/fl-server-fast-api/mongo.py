import os
from enum import Enum
from pathlib import Path
from typing import Any, List, Optional

import pymongo
import yaml
from bson import UuidRepresentation, ObjectId
from pymongo import MongoClient
from pymongo.database import Database


class Collections(str, Enum):
    """MongoDB's collections for different types."""

    GROUPS: str = 'groups'
    CONFIGURATIONS: str = 'configurations'
    STRATEGIES: str = 'strategies'
    PROPOSALS: str = 'proposals'
    USERS: str = 'users'
    ORGANISATIONS: str = 'organisations'
    RESULTS: str = 'results'
    TRAINING_SESSIONS: str = 'training_sessions'


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
        self.db[Collections.CONFIGURATIONS].create_index(["governance_id", ("version", pymongo.DESCENDING)])
        self.db[Collections.RESULTS].create_index(["training_configuration_id"])
        self.db[Collections.TRAINING_SESSIONS].create_index(["training_configuration_id"])



def get_db() -> Database:
    """Get db object."""
    return MongoDB().db