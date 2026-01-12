from tests.unit.conftest import *

def test_create_member(client):
    payload = {
        "name": "TestUser",
        "organization": "HKA",
        "description": "I'm just a test partner!"
    }
    group_id = str(specific_group_json['_id'])
    response = client.post('/groups/' + group_id + '/members',
                           json=payload)
    resp_dict = response.json()
    assert resp_dict["name"] == payload["name"]
    assert resp_dict["organization"] == payload["organization"]
    assert resp_dict["description"] == payload["description"]
    assert response.status_code == 200


def test_get_all_members(client):
    group_id = str(specific_group_json['_id'])
    response = client.get('/groups/' + group_id + '/members')
    resp_dict = response.json()
    assert resp_dict[0]["name"] == "SpecificTestUser"
    assert resp_dict[0]["description"] == "I'm just a test partner!"
    assert response.status_code == 200


def test_get_specific_member(client):
    group_id = str(specific_group_json['_id'])
    member_id = str(specific_members_json['_id'])
    response = client.get(
        '/groups/' + group_id + '/members/' + member_id)
    resp_dict = response.json()
    assert resp_dict["name"] == "SpecificTestUser"
    assert resp_dict["description"] == "I'm just a test partner!"
    assert response.status_code == 200

# def test_delete_member(self):
#    with self.client:
#        group_id = '5bb3314919802578051ccf87'
#        member_id = '5bb3314919802578051ccf87'
#        response = self.client.delete(
#            '/groups/' + group_id + '/members/' + member_id)

#        assert response.status_code == 204
