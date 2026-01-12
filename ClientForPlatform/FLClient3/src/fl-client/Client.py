from logging import INFO

import flwr
from sys import argv
import os

import pandas as pd
from flwr.common.logger import log

# if len(argv) > 6:
# if bool(argv[7]):
#     gpus = tf.config.experimental.list_physical_devices('GPU')
#     try:
#         for gpu in gpus:
#             tf.config.experimental.set_memory_growth(gpu, True)
#     except RuntimeError as e:
#         print(e)

# from SyntheticDataGenerator import sample_synthetic_unlabeled_data
from experiment_parameters.TrainerFactory import strategies_dictionary

"""
Look for similar comments on the Server.py file.
"""

strategy_selected = argv[1]
name_dataset = argv[2]
model_selected = argv[3]
client_id = argv[4]
connection_ip = argv[5]
metric_list = argv[6].split("-")

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
# TODO: If logits are true, than crash
# Function call stack:
# train_function -> assert_greater_equal_Assert_AssertGuard_false_811
# -> train_function -> assert_greater_equal_Assert_AssertGuard_false_811

logits = False
if strategy_selected in ["FedKD", "FedDKD"]:
    logits = True

# model = factory_return_model(dataset_factory, model_selected, logits)

# dataset_name = "\\dataset_" + dataset_selected
# alpha_directory = "\\alpha_" + route_to_dataset

# The training data is retrieved by using the name of the dataset.
working_directory = os.getcwd() + os.sep + "src" + os.sep + "fl-client"
directory_for_training_data = working_directory + os.sep + "data" + os.sep + "training_data_preprocessed"
# directory_for_training_data = working_directory + os.sep + "data" + os.sep + "training_data"
# directory_for_training_data_no_preprocessed = working_directory + os.sep + "data" + os.sep + "training_data"
path_to_train_datasets = directory_for_training_data + os.sep + name_dataset
# path_to_train_datasets_no_pro = directory_for_training_data_no_preprocessed + os.sep + name_dataset

# directory_for_synthetic_data = working_directory + "\\data\\synthetic_data\\dirichlet"
# path_to_synthetic_datasets = directory_for_synthetic_data + dataset_name + alpha_directory
# os.makedirs(path_to_synthetic_datasets, exist_ok=True)

X_train = pd.read_csv(path_to_train_datasets + os.sep + "X_train.csv", index_col=0)
y_train = pd.read_csv(path_to_train_datasets + os.sep + "y_train.csv", index_col=0)
X_test = pd.read_csv(path_to_train_datasets + os.sep + "X_test.csv", index_col=0)
y_test = pd.read_csv(path_to_train_datasets + os.sep + "y_test.csv", index_col=0)
# full_dataframe = X.join(y)


# if "CrossEntropyLoss" not in metric_list:
#     metric_list.append("CrossEntropyLoss")
# if "Accuracy" not in metric_list:
#     metric_list.append("Accuracy")

client_strategy_type = strategies_dictionary[strategy_selected].create_client()
client_strategy = client_strategy_type(model_selected,
                                       X_train,
                                       X_test,
                                       y_train,
                                       y_test,
                                       client_id,
                                       metric_list)

if model_selected == "mlp":
    client_strategy = client_strategy.to_client()

# Start Flower client
flwr.client.start_client(server_address=connection_ip, client=client_strategy)
