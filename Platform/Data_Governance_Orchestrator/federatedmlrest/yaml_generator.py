import asyncio
import json

import yaml
import requests
from requests import Response

from federatedmlrest.api.DBConnection import get_db
from federatedmlrest.api.models.common import PyUUID
from federatedmlrest.lib import getters
from federatedmlrest.api.models import config_models, dataset_models, ml_model_models
from federatedmlrest.api.models.dataset_models import EncodingType, Feature, FeatureType


async def createYaml(strategy, sole_winner, db):
    configuration: config_models.Configuration = getters.find_config(sole_winner, db)
    group = getters.find_group_governance(strategy.belonging_group, db=db)
    members = [str(member) for member in group.members]
    num_clients = len(members)
    dataset: dataset_models.Dataset = getters.find_dataset_governance(configuration.dataset_id,
                                                                      configuration.dataset_version,
                                                                      db=db)
    ml_model: ml_model_models.MLModel = getters.find_ml_model_governance(configuration.ml_model_id,
                                                                         configuration.ml_model_version,
                                                                         db=db)

    ml_model_type = ml_model.model.algorithm
    # Getting Quality Requirements from winner strategy the other strategies are deleted
    quality_requirement_list = []
    for quality_requirement in strategy.quality_requirements:
        quality_requirement_list.append(
            getters.find_quality_requirement(quality_requirement, db=db).quality_requirement.metric
        )

    '''
    Prioritising hyperparameters given from cockpit over default values
    The method hyper_parameter_search expects the name of the hyperparameter, the list of the hyperparameters from the cockpit and default values
    The method assumes, that the hyperparameter list from the model only includes those that have actual values assigned to them
    The method assumes for the format of the hyperparameter list to look something like this: [["model_one_name", [1, 2]], ["model_two_name", [3, 4]]...]
    '''
    hyperparameter_cockpit = ml_model.model.hyperparameters
    hyperparameter = {}
    if ml_model_type == "mlp" or ml_model_type == "tabnet":
        hyperparameter["batchsize"] = hyper_parameter_search("batchsize", hyperparameter_cockpit, [16, 128])
        hyperparameter["learning_rate_init"] = hyper_parameter_search("learning_rate_init", hyperparameter_cockpit,
                                                                      [1e-5, 1e-2])
        hyperparameter["decay_steps"] = hyper_parameter_search("decay_steps", hyperparameter_cockpit, [500, 2000])
        hyperparameter["decay_rate"] = hyper_parameter_search("decay_rate", hyperparameter_cockpit, [0.8, 0.95])

        if ml_model_type == "mlp":
            hyperparameter["num_layers"] = hyper_parameter_search(f'num_layers', hyperparameter_cockpit, [1, 4])
            hyperparameter[f'range_of_units'] = hyper_parameter_search(f'range_of_units', hyperparameter_cockpit, [4, 128])
            hyperparameter[f'dropouts'] = hyper_parameter_search(f'dropouts', hyperparameter_cockpit, [0, 0.4])
            hyperparameter[f'activations'] = hyper_parameter_search(f'activations', hyperparameter_cockpit, ["relu", "tanh"])

        elif ml_model_type == "tabnet":
            hyperparameter["output_dim"] = hyper_parameter_search("output_dim", hyperparameter_cockpit, [4, 512])
            hyperparameter["num_decision_steps"] = hyper_parameter_search("num_decision_steps",
                                                                          hyperparameter_cockpit, [3, 7])
            hyperparameter["sparsity"] = hyper_parameter_search("sparsity", hyperparameter_cockpit, [1e-5, 1e-3])
            hyperparameter["batch_momentum"] = hyper_parameter_search("batch_momentum", hyperparameter_cockpit,
                                                                      [0.8, 1])
            hyperparameter["relaxation_factor"] = hyper_parameter_search("relaxation_factor",
                                                                         hyperparameter_cockpit, [1, 3])
    elif ml_model_type == "xgboost":
        hyperparameter["tree_method"] = hyper_parameter_search("tree_method", hyperparameter_cockpit, "hist")
        hyperparameter["booster"] = hyper_parameter_search("booster", hyperparameter_cockpit, "gbtree")
        hyperparameter["eta"] = hyper_parameter_search("eta", hyperparameter_cockpit, [0.01, 0.2])
        hyperparameter["max_depth"] = hyper_parameter_search("max_depth", hyperparameter_cockpit, [2, 10])
        hyperparameter["gamma"] = hyper_parameter_search("gamma", hyperparameter_cockpit, [0, 0.2])
        hyperparameter["subsample"] = hyper_parameter_search("subsample", hyperparameter_cockpit, 1)
        hyperparameter["max_delta_step"] = hyper_parameter_search("max_delta_step", hyperparameter_cockpit, [0, 10])
        hyperparameter["lambda"] = hyper_parameter_search("lambda", hyperparameter_cockpit, [0, 2])
        hyperparameter["min_child_weight"] = hyper_parameter_search("min_child_weight", hyperparameter_cockpit,
                                                                    [1, 6])
        hyperparameter["seed"] = hyper_parameter_search("seed", hyperparameter_cockpit, 1)

    strategy_name = "FedAvg"
    if ml_model_type == "xgboost":
        strategy_name = "FedXGB"

    '''
    Add the preprocessing option, with the following options:

    Type of Preprocessing:

    For Categorical: Label Encoder

    For numerical: Standard Scale or Min Max (Enum)

    Secure: Boolean. True by Default.
    '''
    # Getting dataset features and putting them in nested list for yaml
    dataset_features = []
    dataset_input_size = 0
    dataset_output_size = 0
    for feature in dataset.features:
        preprocessing_option, generated_dimensions = set_preprocessing_options(feature)
        if feature.name == "label":
            dataset_output_size += generated_dimensions
        else:
            dataset_input_size += generated_dimensions

        if feature.type == "string":
            newFeature = {
                'name': feature.name,
                'type': feature.type,
                'valid_values': feature.valid_values,
                'order_in_dataset': feature.order_in_dataset,
                'preprocessing': preprocessing_option
            }
        else:
            newFeature = {
                'name': feature.name,
                'type': feature.type,
                'range': feature.valid_values,
                'order_in_dataset': feature.order_in_dataset,
                'preprocessing': preprocessing_option
            }
        dataset_features.append(newFeature)

    data = {
        'configuration_id': str(sole_winner),
        'group_members': members,
        'strategy': strategy_name,
        'metric_name': quality_requirement_list,
        'dataset': dataset.name,
        'validation_configuration': {
            'dataset_features': dataset_features
        },
        'dataset_input_size': dataset_input_size,
        'dataset_output_size': dataset_output_size,
        'model': ml_model_type,
        'hyperparameter_space': hyperparameter,
        'rounds': configuration.number_of_rounds,
        'hyperparameter_search': True,
        'hyperparameter_search_rounds': configuration.number_of_ho_rounds,
        'model_final_name': str(sole_winner),
        'compute_shapley_values': 0,
        'connection_ip': 'localhost:54080',
        'number_clients': num_clients
    }

    with open("federatedmlrest/config.yml", "r") as f:
        secrets = yaml.safe_load(f)

    response: Response = requests.post("http://kc:8080/auth/realms/fml/protocol/openid-connect/token",
                                       data={
                                           "grant_type": "client_credentials",
                                           "client_id": secrets["keycloak"]["api_client_id"],
                                           "client_secret": secrets["keycloak"]["api_client_secret"]
                                       })
    access_token = response.json()['access_token']

    # write_yaml_to_file(data, 'configuration')
    requests.post('http://fl-server-fastapi:20000/upload_configuration',
                  headers={'Authorization': 'Bearer ' + access_token},
                  data = json.dumps(data))
                  # files={"file": ("training_configuration", str(data), "application/json")})


def set_preprocessing_options(feature: Feature):
    if feature.preprocessing == EncodingType.NONE:
        return {
            "type_of_Preprocessing": "none",
            "Secure": False
        }, 1
    # elif feature.type in [FeatureType.INTEGER, FeatureType.LONG, FeatureType.FLOAT, FeatureType.DOUBLE]:
    elif feature.preprocessing == EncodingType.MIN_MAX_ENCODER:
        return {
            "type_of_Preprocessing": "min_max_encoder",
            "Secure": True
        }, 1
    elif feature.preprocessing == EncodingType.STANDARD_ENCODER:
        return {
            "type_of_Preprocessing": "standard_encoder",
            "Secure": True
        }, 1
    # return None
    # elif feature.type == FeatureType.STRING:
    elif feature.preprocessing == EncodingType.ONE_HOT_ENCODER:
        return {
            "type_of_Preprocessing": "one_hot_encoder",
            "Secure": True
        }, len(feature.valid_values)
    elif feature.preprocessing == EncodingType.LABEL_ENCODER:
        return {
            "type_of_Preprocessing": "label_encoder",
            "Secure": True
        }, 1
    return None
    # return None


def write_yaml_to_file(py_obj, filename):
    with open(f'{filename}.yaml', 'w') as f:
        yaml.dump(py_obj, f, default_flow_style=None, sort_keys=False)
    print('written to file successfully')


def hyper_parameter_search(name, hyperparameter_values, default_values):
    for hyperparameter in hyperparameter_values:
        if name == hyperparameter.name:
            return hyperparameter.valid_values

    return default_values


if __name__ == "__main__":
    # with open("federatedmlrest/config.yml", "r") as f:
    #     secrets = yaml.safe_load(f)
    # response: Response = requests.post("http://localhost/auth/realms/fml/protocol/openid-connect/token",
    #                                    data={
    #                                        "grant_type": "client_credentials",
    #                                        "client_id": secrets["keycloak"]["api_client_id"],
    #                                        "client_secret": secrets["keycloak"]["api_client_secret"]
    #                                    })
    # access_token = response.json()['access_token']
    strategy = getters.find_strategy_governance(PyUUID("5c9cdec8-37a2-4bbc-8a09-3d9eff14fb98"))
    configuration = getters.find_config(strategy.configurations[0])
    asyncio.run(createYaml(strategy, configuration.id, get_db()))