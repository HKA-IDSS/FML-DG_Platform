from tests.unit.conftest import *


strat_payload = {
    "name": "TestStrategy",
}

group_id = str(specific_group_json['_id'])
strategy_id = str(specific_strat_json['_id'])


def test_create_strategy(client):
    response = client.post('/groups/' + group_id + '/strategies',
                                json=strat_payload)
    resp_dict = response.json()
    assert response.status_code == 200
    assert resp_dict["name"] == "TestStrategy"
    assert resp_dict["quality_requirements"] == []
    assert resp_dict['configurations'] == []

    _id = str(resp_dict['_id'])
    res = client.delete('/groups/' + group_id + '/strategies/'+ _id)
    assert res.status_code == 204

def test_get_strategies(client):
    response = client.get('/groups/' + group_id + '/strategies')
    resp_dict = response.json()
    assert response.status_code == 200
    assert resp_dict[0]["name"] == "SpecificTestStrategy"
    assert resp_dict[0]["quality_requirements"] == [str(specific_qr_json['_id'])]

def test_get_specific_strategy(client):
    response = client.get(
        '/groups/' + group_id + '/strategies/' + strategy_id)
    resp_dict = response.json()
    assert response.status_code == 200
    assert resp_dict["name"] == "SpecificTestStrategy"
    assert resp_dict["quality_requirements"] == [str(specific_qr_json['_id'])]

# def test_delete_strategy(self):
#    pass
