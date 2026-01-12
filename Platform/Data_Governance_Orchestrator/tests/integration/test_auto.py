import mongomock
import pytest
import schemathesis
from bson import ObjectId
from hypothesis import settings
from starlette_testclient import TestClient

from federatedmlrest.api import dependencies
from federatedmlrest.main import app


db = mongomock.MongoClient().db

app.dependency_overrides[dependencies.get_db] = lambda: db
client = TestClient(app)

schema = schemathesis.from_asgi(app=app, schema_path='/openapi.json')


@schema.parametrize()
@settings(max_examples=10)
def test_auto(case):

    if case.endpoint.path.startswith('/proposal'):
        pytest.skip('To many ID related dependencies.')

    if case.path_parameters:
        update = {}

        for key, value in case.path_parameters.items():
            if key.endswith('_id'):
                update[key] = ObjectId()

        case.path_parameters.update(update)

    case.call_and_validate(session=client)



