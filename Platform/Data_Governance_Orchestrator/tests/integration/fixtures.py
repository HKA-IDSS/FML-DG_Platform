
import mongomock
from starlette.testclient import TestClient

from federatedmlrest import main
from federatedmlrest.api import dependencies

db = mongomock.MongoClient().db

def get_client():
    main.app.dependency_overrides[dependencies.get_db] = lambda: db
    return TestClient(main.app)