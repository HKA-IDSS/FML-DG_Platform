import os

import mongomock
import pytest

from federatedmlrest import main
from federatedmlrest.api import dependencies
from federatedmlrest.mongo import MongoDB
from bson import ObjectId
from fastapi.testclient import TestClient
db = mongomock.MongoClient().db

@pytest.fixture
def client():
    main.app.dependency_overrides[dependencies.get_db] = lambda: db
    return TestClient(main.app)


groups = db['groups']
hyperparameter = db['hyperparameter']
mlmodels = db['mlmodels']
strategies = db['strategies']
members = db['members']
datasets = db['datasets']
configurations = db['configurations']
qrs = db['quality_requirements']

group_json = {
    '_id': ObjectId('64008d32b881e88d19c7e2e6'),
    'description': 'A Group for testing',
    'members': [ObjectId('64008f58b881e88d19c7e2f1')],
    'name': 'TestGroup',
    'strategies': [ObjectId('64008d94b881e88d19c7e2e8')]
}
specific_group_json = {
    '_id': ObjectId('64008d81b881e88d19c7e2e7'),
    'description': 'A specific Group for testing',
    'members': [ObjectId('64008f62b881e88d19c7e2f2')],
    'name': 'SpecificTestGroup',
    'strategies': [ObjectId('64008daab881e88d19c7e2e9')]
}
strat_json = {
    "_id": ObjectId('64008d94b881e88d19c7e2e8'),
    "comments": [],
    "configurations": [ObjectId("64008dd6b881e88d19c7e2ea")],
    "description": "",
    "name": "TestStrategy",
    "quality_requirements": [ObjectId('6400946fb881e88d19c7e2f6')],
}

qr_json = {
    '_id': ObjectId('6400946fb881e88d19c7e2f6'),
    'correctness': {
        'metric': 'testMetric',
        'required_min_value': 0,
        'required_max_value': 10,
    },
}


specific_strat_json = {
    "_id": ObjectId('64008daab881e88d19c7e2e9'),
    "comments": [],
    "configurations": ["64008de9b881e88d19c7e2eb"],
    "description": "",
    "name": "SpecificTestStrategy",
    "quality_requirements": [ObjectId('640094f5b881e88d19c7e2f7')],
}

specific_qr_json = {
    '_id': ObjectId('640094f5b881e88d19c7e2f7'),
    'correctness': {
        'metric': 'testMetric',
        'required_min_value': 0,
        'required_max_value': 10,
    },
}

ml_json = {
    "_id": ObjectId('64008edeb881e88d19c7e2ec'),
    "name": "TestMlModel",
    "algorithm": "PlaceholderAglorithm",
    "framework": "PlaceholderFramework",
    "framework_version": "0.8.15"
}
specific_ml_json = {
    "_id": ObjectId('64008ef6b881e88d19c7e2ed'),
    "name": "SpecificTestMlModel",
    "algorithm": "PlaceholderAglorithm",
    "framework": "PlaceholderFramework",
    "framework_version": "0.8.15"
}
hyper_json = {
    "_id": ObjectId('64008f85b881e88d19c7e2f3'),
    "name": "TestParameter",
    "value": "PlaceholderValue"
}
specific_hyper_json = {
    "_id": ObjectId('64008fa3b881e88d19c7e2f4'),
    "name": "SpecificTestParameter",
    "value": "SpecificPlaceholderValue"
}
unused_hyper_json = {
    "_id": ObjectId('64008facb881e88d19c7e2f5'),
    "name": "SpecificTestParameter",
    "value": "SpecificPlaceholderValue"
}
members_json = {
    "_id": ObjectId('64008f58b881e88d19c7e2f1'),
    "name": "TestUser",
    "organization": "HKA",
    "description": "I'm just a test partner!"
}
specific_members_json = {
    "_id": ObjectId('64008f62b881e88d19c7e2f2'),
    "name": "SpecificTestUser",
    "organization": "HKA",
    "description": "I'm just a test partner!"
}
dataset_json = {
    "_id": ObjectId('64008f21b881e88d19c7e2ef'),
    "name": "TestDataset",
    "description": "Testing datasets!",
    "features": [
        {"name": "Feature1",
         "type": "string",
         "valid_values": ["a", "b"],
         "order_in_dataset": 0,
         "group": False,
         "sub_features": []

         },
        {"name": "Feature2",
         "type": "integer",
         "valid_values": [1, 2],
         "order_in_dataset": 1,
         "group": False,
         "sub_features": []
         }
    ]
}
specific_dataset_json = {
    "_id": ObjectId('64008f35b881e88d19c7e2f0'),
    "name": "SpecificTestDataset",
    "description": "Testing datasets!",
    "features": [
        {"name": "Feature1",
         "type": "string",
         "valid_values": ["a", "b"],
         "order_in_dataset": 0,
         "group": False,
         "sub_features": []

         },
        {"name": "Feature2",
         "type": "integer",
         "valid_values": [1,2],
         "order_in_dataset": 1,
         "group": False,
         "sub_features": []
         }
    ]
}
unused_dataset_json = {
    "_id": ObjectId('64008f15b881e88d19c7e2ee'),
    "name": "UnusedTestDataset",
    "description": "Testing datasets!",
    "features": [
        {"name": "Feature1",
         "type": "string",
         "valid_values": ["a", "b"],
         "order_in_dataset": 0,
         "group": False,
         "sub_features": []

         },
        {"name": "Feature2",
         "type": "integer",
         "valid_values": [1, 2],
         "order_in_dataset": 1,
         "group": False,
         "sub_features": []
         }
    ]
}
configurations_json = {
    "_id": ObjectId('64008dd6b881e88d19c7e2ea'),
    "ml_model_id": ObjectId('64008edeb881e88d19c7e2ec'),
    "dataset_id": ObjectId('64008f21b881e88d19c7e2ef')
}
specific_configurations_json = {
    "_id": ObjectId('64008de9b881e88d19c7e2eb'),
    "ml_model_id": ObjectId("64008ef6b881e88d19c7e2ed"),
    "dataset_id": ObjectId("64008f35b881e88d19c7e2f0")
}


def pytest_configure():
    collections = db.list_collection_names()
    for collection in collections:
        db[collection].drop()

    groups.insert_one(group_json)
    groups.insert_one(specific_group_json)

    members.insert_one(members_json)
    members.insert_one(specific_members_json)

    strategies.insert_one(strat_json)
    strategies.insert_one(specific_strat_json)

    mlmodels.insert_one(ml_json)
    mlmodels.insert_one(specific_ml_json)

    hyperparameter.insert_one(hyper_json)
    hyperparameter.insert_one(specific_hyper_json)
    hyperparameter.insert_one(unused_hyper_json)

    datasets.insert_one(dataset_json)
    datasets.insert_one(specific_dataset_json)
    datasets.insert_one(unused_dataset_json)

    configurations.insert_one(configurations_json)
    configurations.insert_one(specific_configurations_json)

    qrs.insert_one(qr_json)
    qrs.insert_one(specific_qr_json)

