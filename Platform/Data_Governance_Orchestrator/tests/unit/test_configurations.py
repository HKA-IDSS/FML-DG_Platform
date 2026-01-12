from tests.unit.conftest import *

strat_payload = {
    "ml_model_id": str(ml_json['_id']),
    "dataset_id": str(dataset_json['_id'])
}



def test_create_configuration(client):
    group_id = str(group_json['_id'])
    strat_id = str(strat_json['_id'])
    response = client.post(
        '/groups/' + group_id + '/strategies/' + strat_id +
        '/configurations',
        json=strat_payload)
    resp_dict = response.json()
    assert response.status_code == 200
    assert resp_dict['dataset_id'] == str(dataset_json['_id'])
    assert resp_dict['ml_model_id'] == str(ml_json['_id'])

def test_get_configurations(client):
    group_id = str(group_json['_id'])
    strat_id = str(strat_json['_id'])
    response = client.get(
        '/groups/' + group_id + '/strategies/' + strat_id +
        '/configurations')
    resp_dict = response.json
    assert response.status_code == 200
    assert resp_dict

def test_get_specific_configuration(client):
    group_id = str(specific_group_json['_id'])
    strat_id = str(specific_strat_json['_id'])
    conf_id = str(specific_configurations_json['_id'])
    response = client.get(
        '/groups/' + group_id + '/strategies/' + strat_id +
        '/configurations/' + conf_id)
    resp_dict = response.json()
    assert response.status_code == 200
    assert resp_dict

    # def test_delete_strategy():
    #    pass
