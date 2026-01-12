import os.path
from os import listdir
from os.path import isfile, join
from uuid import UUID

import requests
from requests import Response
import yaml

from flwr.common.logger import log
from logging import WARNING, INFO

def get_token():
    log(INFO, f"Current directory: {os.getcwd()}")
    with open("src/fl-server-fast-api/flower_server/secrets.yaml", "r") as f:
        secrets = yaml.safe_load(f)

    response: Response = requests.post("http://kc:8080/auth/realms/fml/protocol/openid-connect/token",
                                 data={
                                     "grant_type": "client_credentials",
                                     "client_id": "flower-server",
                                     "client_secret": secrets["keycloak_secret"]
                                 })
    access_token = response.json()['access_token']
    return access_token


def send_results_to_governance_platform(training_configuration, type_of_model: str = "mlp"):
    token = get_token()
    directory = "results" + os.sep + training_configuration
    list_of_files = [{f: os.path.join(directory + '/Evaluation', f)}
                     for f in listdir(directory + '/Evaluation')
                     if isfile(join(directory + '/Evaluation', f))]
    list_of_sv_files = []
    if os.path.isdir(directory + '/Shapley_Value'):
        list_of_sv_files = [{f: os.path.join(directory + '/Shapley_Value', f)}
                            for f in listdir(directory + '/Shapley_Value')
                            if isfile(join(directory + '/Shapley_Value', f))]
    list_of_files = list_of_files + list_of_sv_files
    for evaluation_file in list_of_files:
        for filename, file in evaluation_file.items():
            with open(file, "rb") as f:
                requests.post('http://rest-api:5100/api1/results/evaluations/' + training_configuration,
                              headers={'Authorization': 'Bearer ' + token},
                              files={"file": (filename, f, "application/csv")})

    if type_of_model == "xgboost":
        model_name = training_configuration + ".json"
    else:
        model_name = training_configuration + ".keras"

    model_file = "results/model/" + model_name
    with open(model_file, "rb") as f:
        requests.post('http://rest-api:5100/api1/results/models/' + training_configuration,
                      headers={'Authorization': 'Bearer ' + token},
                      files={"file": (model_name, f, "application/file")})

    # with open("configuration.yaml", "r") as f:
    #     configuration = yaml.safe_load(f)

    # requests.post('http://rest-api:5100/api1/results/training_information',
    #               headers={'Authorization': 'Bearer ' + token},
    #               json={
    #                   "configuration_id": configuration["configuration_id"],
    #                   "metric_used": configuration["metric_name"],
    #                   "shapley_values": True if configuration["compute_shapley_values"] == 1 else False
    #               })


if __name__ == "__main__":
    with open("../secrets.yaml", "r") as f:
        secrets = yaml.safe_load(f)
