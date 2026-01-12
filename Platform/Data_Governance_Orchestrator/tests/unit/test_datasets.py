from tests.unit.conftest import *

data_payload = {
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
    ],
}
change_payload = [{"name": "Changed Feature",
                   "type": "float",
                   "valid_values": [0.2, 0.3],
                   "order_in_dataset": 0,
                   "description": "This one is a better feature",
                   "other_info": "Is better!",
                   "group": False,
                   "sub_features":[]}]


class TestDatasetsResource:

    def test_create_dataset(self, client):
        response = client.post('/datasets', json=data_payload)
        resp_dict = response.json()
        assert response.status_code == 200
        assert resp_dict
        assert resp_dict['name'] == "TestDataset"

    def test_get_datasets(self, client):
        response = client.get('/datasets')
        resp_dict = response.json()
        assert response.status_code == 200
        assert resp_dict
        assert resp_dict[0]['_id'] == str(dataset_json['_id'])
        assert resp_dict[0]['name'] == dataset_json['name']
        assert resp_dict[1]['_id'] == str(specific_dataset_json['_id'])
        assert resp_dict[1]['name'] == specific_dataset_json['name']

    def test_get_specific_dataset(self, client):
        data_id = str(specific_dataset_json['_id'])
        response = client.get('/datasets/' + data_id)
        resp_dict = response.json()
        assert response.status_code == 200
        assert resp_dict
        assert resp_dict['_id'] == str(specific_dataset_json['_id'])
        assert resp_dict['name'] == specific_dataset_json['name']


    def test_delete_dataset_in_use(self, client):
        data_id = str(unused_dataset_json['_id'])
        response = client.delete('/datasets/' + data_id)
        assert response.status_code == 204

    def test_delete(self, client):
        data_id = str(specific_dataset_json['_id'])
        response = client.delete('/datasets/' + data_id)
        assert response.status_code == 409


class TestFeaturesResource:

    def test_change_features(self, client):
        data_id = str(dataset_json['_id'])
        response = client.put('/datasets/' + data_id + '/features',
                                   json=change_payload)
        resp_dict = response.json()
        assert response.status_code == 200
        assert resp_dict
        assert resp_dict['_id'] == str(dataset_json['_id'])
        assert resp_dict['features'][0]['name'] == 'Changed Feature'

    def test_get_features(self,client):
        data_id = str(specific_dataset_json['_id'])
        response = client.get('/datasets/' + data_id)
        resp_dict = response.json()
        assert response.status_code == 200
        assert resp_dict['_id'] == str(specific_dataset_json['_id'])
        assert resp_dict['name'] == 'SpecificTestDataset'
        assert resp_dict['features'][0]['name'] == 'Feature1'
