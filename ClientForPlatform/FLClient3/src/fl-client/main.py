import asyncio
import hashlib
import json
import os
import subprocess
import sys
import datetime
from functools import reduce

import pandas as pd

import requests
from requests import Response
from sklearn.model_selection import train_test_split
from websockets import connect
from util.SimplePreprocessing import scale_column, one_hot_encode_column
from util.GreatExpectationService import GreatExpectationService
from util.GEHtmlService import GEHtmlService


async def register_dataset(access_token, session_to_participate, selected_dataset):
    async with connect(f"ws://localhost/api2/register_dataset/{session_to_participate}",
                       additional_headers={"Authorization": 'Bearer ' + access_token}) as websocket:
                       # subprotocols=["Bearer", f"Bearer {access_token}"]) as websocket:
        expectations_string = await websocket.recv()
        print(expectations_string)
        # expectations_string = request.great_expectations_suite.decode('utf-8')
        expectations = json.loads(expectations_string)

        expectationService = GreatExpectationService()
        expectationService.add_expectations_from_configuration(expectations)


        pandas_dataset = pd.read_csv("src/fl-client/data/datasets_to_register/" + selected_dataset, index_col=0)
        groups_of_columns = list(pandas_dataset.select_dtypes(include=['str']).columns)
        for column in groups_of_columns:
            pandas_dataset[column] = pandas_dataset[column].astype("string")


        # Run validation on specified dataset
        validation_result = expectationService.run_validation_on_pandas(pandas_dataset)
        await websocket.send(str(validation_result.success))
        if validation_result.success:
            os.makedirs("src/fl-client/data/registered_datasets", exist_ok=True)
            df = pd.read_csv("src/fl-client/data/datasets_to_register/" + selected_dataset, index_col=0)
            dataset_hash = str(int(hashlib.sha256(pd.util.hash_pandas_object(df, index=True).values).hexdigest(), 16))
            await websocket.send(dataset_hash)
            df.to_csv("src/fl-client/data/registered_datasets/" + dataset_hash + ".csv")
        else:
            # Create HTML and JSON results
            filename = f"{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}_validation_results.json"
            os.makedirs("src/fl-client/tmp", exist_ok=True)
            filepath = os.path.join("src/fl-client/tmp", filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(validation_result.to_json_dict(), f, indent=2, ensure_ascii=False)
            reporter = GEHtmlService()
            report_path = reporter.build_and_save_html(validation_result.to_json_dict())
            print(f"HTML report saved to: {report_path}")


async def preprocessing(hash_dataset, features_information):
    valid_dataset = pd.read_csv("src/fl-client/data/registered_datasets/" + hash_dataset + ".csv", index_col=0)
    y = valid_dataset.iloc[:,-1:]
    X = valid_dataset

    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=1, test_size=0.3)

    preprocessed_X_train = pd.DataFrame()
    preprocessed_X_test = pd.DataFrame()
    preprocessed_y_train = pd.DataFrame()
    preprocessed_y_test = pd.DataFrame()

    label_column_name = features_information[-1]["name"]

    for feature in features_information:
        # if feature["type"] == "integer" or feature["type"] == "float":
        if feature["preprocessing"]["type_of_Preprocessing"] == "min_max_encoder":
            if feature["name"] == label_column_name:
                scaled_column_train = scale_column(y_train, feature["range"][0],
                                                   feature["range"][1])
                scaled_column_test = scale_column(y_test, feature["range"][0], feature["range"][1])
                preprocessed_y_train = scaled_column_train
                preprocessed_y_test = scaled_column_test
            else:
                scaled_column_train = scale_column(X_train[feature["name"]], feature["range"][0], feature["range"][1])
                scaled_column_test = scale_column(X_test[feature["name"]], feature["range"][0], feature["range"][1])
                preprocessed_X_train[feature["name"]] = scaled_column_train
                preprocessed_X_test[feature["name"]] = scaled_column_test

        # if feature["type"] == "string":
        if feature["preprocessing"]["type_of_Preprocessing"] == "one_hot_encoder":
            # transformed_columns = one_hot_encode_column(feature["name"], feature["valid_values"])
            if feature["name"] == label_column_name:
                transformed_columns_train = one_hot_encode_column(y_train[feature["name"]], feature["valid_values"])
                transformed_columns_test = one_hot_encode_column(y_test[feature["name"]], feature["valid_values"])
                preprocessed_y_train = transformed_columns_train
                preprocessed_y_test = transformed_columns_test
            else:
                transformed_columns_train = one_hot_encode_column(X_train[feature["name"]], feature["valid_values"])
                transformed_columns_test = one_hot_encode_column(X_test[feature["name"]], feature["valid_values"])
                preprocessed_X_train = pd.merge(left=preprocessed_X_train, right=transformed_columns_train,
                                                 left_index=True, right_index=True)
                preprocessed_X_test = pd.merge(left=preprocessed_X_test, right=transformed_columns_test,
                                                left_index=True, right_index=True)

    os.makedirs("src/fl-client/data/training_data_preprocessed/" + hash_dataset, exist_ok=True)
    preprocessed_X_train.to_csv("src/fl-client/data/training_data_preprocessed/" + hash_dataset + os.sep + "X_train.csv")
    preprocessed_X_test.to_csv("src/fl-client/data/training_data_preprocessed/" + hash_dataset + os.sep + "X_test.csv")
    preprocessed_y_train.to_csv("src/fl-client/data/training_data_preprocessed/" + hash_dataset + os.sep + "y_train.csv")
    preprocessed_y_test.to_csv("src/fl-client/data/training_data_preprocessed/" + hash_dataset + os.sep + "y_test.csv")


async def join_training(access_token, session_to_participate):
    async with connect(f"ws://localhost/api2/join_training/{session_to_participate}",
                       additional_headers={"Authorization": 'Bearer ' + access_token}) as websocket:
        message = await websocket.recv()
        print(message)  # It should be "JoiningTraining" now
        # message = "Start Clients"
        while message != "CloseConnection":
            if message == "JoiningTraining":
                subscribed_dataset_hash = await websocket.recv()
                await websocket.send("SubscriptionFinished")

            elif message == "PerformPreprocessing":
                dataset_features = json.loads(await websocket.recv())
                print(type(dataset_features))
                await preprocessing(subscribed_dataset_hash, dataset_features)
                print("Sending Preprocessing Finished")
                await websocket.send("PreprocessingFinished")

            elif message == "SendingParameters":
                await websocket.send("SendMeParameters")
                training_parameters: dict = json.loads(await websocket.recv())

                strategy = training_parameters["strategy"]
                name_dataset = training_parameters["name_dataset"]
                model_selected = training_parameters["model_selected"]
                client_number = username
                connection_ip = training_parameters["connection_ip"]
                metric_list = training_parameters["metric_name"]
                metrics_string = reduce(lambda metric1, metric2: metric1 + "-" + metric2, metric_list)

                print("ParametersReceived")
                await websocket.send("ParametersReceived")

            elif message == "StartClient":
                print("Starting Training")
                training_process = subprocess.Popen(['python',
                                                     'src/fl-client/Client.py',
                                                     strategy,
                                                     name_dataset,
                                                     model_selected,
                                                     str(client_number),
                                                     connection_ip,
                                                     metrics_string],
                                                    stdout=sys.stdout)  # If linux, remove creationflags
                await asyncio.sleep(3)
                while training_process.poll() is None:
                    await websocket.send("Unfinished")
                    await asyncio.sleep(10)
                # training_process.wait()
                print("Waiting for training")
                await asyncio.sleep(3)
                await websocket.send("TrainingFinished")
                print("TrainingFinished")
                await websocket.send("NextRound?")


            else:
                await websocket.close()

            message = await websocket.recv()
            print(message)


def main(username_auth, password_auth):
    response: Response = requests.post("http://localhost/auth/realms/fml/protocol/openid-connect/token",
                                       data={
                                           "client_id": "fl-client",
                                           "grant_type": "password",
                                           "username": username_auth,
                                           "password": password_auth
                                       })
    return response.json()["access_token"]

# async def ws_trial(access_token):
#     async with connect("ws://localhost/api2/ws-test",
#                        additional_headers={"Authorization": 'Bearer ' + access_token}) as ws:
#         print(await ws.recv())

if __name__ == "__main__":
    username = input("Enter your username:")
    password = input("Enter your password:")
    token = main(username, password)
    while True:
        option_selected = input("Please, select what you would like to do:\n"
                                "1: Check possible training sessions.\n"
                                "2: Register a dataset to an existing training session.\n"
                                "3: Participate on a training session.\n"
                                "4: Quit the program.\n")
        if option_selected == "1":
            response: Response = requests.get("http://localhost/api2/training_sessions",
                                              headers={'Authorization': 'Bearer ' + token})
            print(response.text)
        elif option_selected == "2":
            session_selected = input("Introduce the session in which you want to participate.\n")
            print("List of datasets that you can register:")
            print(os.listdir("src/fl-client/data/datasets_to_register"))
            selected_dataset = input("Please, select the dataset that you want to register.\n")
            asyncio.run(register_dataset(token, session_selected, selected_dataset))
        elif option_selected == "3":
            session_selected = input("Introduce the session in which you want to participate.\n")
            asyncio.run(join_training(token, session_selected))
        elif option_selected == "4":
            print("Exiting")
            exit(0)
        else:
            print("Invalid option")
