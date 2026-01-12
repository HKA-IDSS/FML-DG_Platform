from tests.unit.conftest import *


def test_create_group(client):
    payload = {
        "name": "Test Group",
        "description": "A Group for testing"
    }
    response = client.post('/groups', json=payload)
    resp_dict = response.json()

    assert response.status_code == 200
    assert resp_dict["name"] == payload["name"]
    assert resp_dict["description"] == payload["description"]

def test_get_all_groups(client):
    response = client.get('/groups')
    resp_dict = response.json()
    assert response.status_code == 200
    assert resp_dict

def test_get_specific_group(client):
    group_id = str(specific_group_json['_id'])
    response = client.get('/groups/' + group_id)
    resp_dict = response.json()
    assert response.status_code == 200
    assert resp_dict["name"] == 'SpecificTestGroup'
    assert resp_dict["description"] == 'A specific Group for testing'

# def test_delete_group(client):
#    group_id = '5bb3314919802578051ccf86'
#    delete_response = client.delete('/groups/' + group_id)
#    assert delete_response.status_code == 204
