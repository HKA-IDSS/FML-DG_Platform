from tests.unit.conftest import *

payload = {
    "name": "TestMlModel",
    "algorithm": "PlaceholderAglorithm",
    "framework": "PlaceholderFramework",
    "framework_version": "0.8.15",
    "hyperparameter": [
        {
            "name": "TestParameter",
            "value": "PlaceholderValue"
        }
    ],
}


def test_create_ml_model(client):
    response = client.post('/ml-models', json=payload)
    resp_dict = response.json()
    assert response.status_code == 200
    assert resp_dict["name"] == payload["name"]
    assert resp_dict["algorithm"] == payload["algorithm"]
    assert resp_dict["framework"] == payload["framework"]
    assert resp_dict["framework_version"] == payload[
        "framework_version"]
    assert resp_dict['hyperparameter'] == payload['hyperparameter']

def test_get_all_models(client):
    response = client.get('/ml-models')
    assert response.status_code == 200

def test_get_specific_model(client):
    model_id = str(specific_ml_json['_id'])
    response = client.get(
        '/ml-models/' + model_id)
    resp_dict = response.json()
    assert response.status_code == 200
    assert resp_dict["name"] == "SpecificTestMlModel"
