import ast
from logging import INFO
from sys import argv

import flwr as fl
import keras
from flwr.server.strategy import FedXgbBagging
from keras import layers
import tensorflow as tf

from flwr.common.logger import log
from flower.FedAvgRewritten import FedAvgRewritten

# from experiment_parameters.TrainerFactory import strategies_dictionary, factory_return_model, dataset_model_dictionary
# from experiment_parameters.model_builder.Model import XGBoostModel
# from experiment_parameters.model_builder.ModelBuilder import get_training_configuration, Director
from flower.Model import KerasModel, XGBoostModel
from flower.Evaluator import evaluator
# from metrics.GradientRewards import GradientRewards
from flower.Metrics import return_default_dict_of_metrics
# from metrics.Shapley_Values import ShapleyValuesNN, ShapleyValuesDT
# from flower import OptunaConnection

def load_model(learning_rate: float = 0.001):
    model = keras.Sequential(
        [
            keras.Input(shape=(13, )),
            layers.Dense(16, activation="relu"),
            layers.Dense(8, activation="relu"),
            layers.Dense(3, activation="softmax")
        ]
    )
    model.compile(
        "adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model

# Either Keras Model, or XGBoost.
model = KerasModel(load_model())
weights = model.get_model().get_weights()
parameters = fl.common.ndarrays_to_parameters(weights)
strategy_selected = FedAvgRewritten

# model = XGBoostModel()
# parameters = None
# parameters_dict = None
# strategy_selected = FedXgbBagging

possible_outputs = ["Red", "White", "Sparkling"]

# input_dim = int(argv[4])
# output_dim = int(argv[5])
number_of_clients = 2
number_of_rounds = 20
metric_list = ["CrossEntropyLoss", "Accuracy"]

# study = OptunaConnection.load_study(model_final_name)
#
# if load_best_trial == 0:
#     trial = study.ask()
#     parameters_dict = get_training_configuration(trial, model_selected)
#
# elif load_best_trial == 1:
#     trial = None  # Quickfix. Not so nicely programmed.
#     trial_with_highest_accuracy = study.best_trial
#     parameters_dict = get_training_configuration(trial_with_highest_accuracy, model_selected)
# Dataset factory. In this case, because the dataset is not used directly in this file,
# it is not instantiated. This factory is used by the strategy, to pass the data for
# evaluation.
# dataset_factory = dataset_model_dictionary[dataset_selected]()
# x_test, y_test = dataset_factory.get_dataset().get_test_data()

# Try to use the config for sending the parameters.
def get_fit_config_func(parameters_dict):
    def fit_config_func(server_round):
        config = {
            "server_round": server_round,
            "gradient_tracking": 0
        }
        # if server_round == 1:
        #     config.update(parameters_dict)
        #     log(INFO, "Updating config: {}".format(parameters_dict))
        return config

    return fit_config_func


# Try to use the config for sending the parameters.
def get_evaluate_config_func(compute_shapley_values, num_rounds):
    def evaluate_config_func(server_round):
        config = {
            "server_round": server_round,
            "compute_shapley_values": compute_shapley_values,
            "num_rounds": num_rounds
        }

        return config

    return evaluate_config_func


# This is just to get the model prepared for KD.
# logits = False
# if strategy_selected in ["FedKD", "FedDKD"]:
#     logits = True

# log(INFO, "Logits: {}".format(logits))
# This is the model. For retrieving the model class (type of instance TFModel)
# from the file Model.py.


# director = Director()


# Strategies are retrieved from the factory, which is retrieved using the string on the dictionary.
# Then, a type of the class of the strategy is returned. It needs to be instantiated afterwards
# by passing all the parameters.
# There are multiple new parameters on strategies:
#   Dataset_factory, for retrieving data for evaluation.
#   TFModel
#   Shapley Values: To enable the computation. (Currently obligatory, but no need to call the function)
#   Accuracy

# if "CrossEntropyLoss" not in metric_list:
#     metric_list.append("CrossEntropyLoss")
# if "Accuracy" not in metric_list:
#     metric_list.append("Accuracy")

strategy = FedAvgRewritten(
    # ... other fedavg arguments
    max_round=number_of_rounds,
    possible_outputs=possible_outputs,
    model=model,
    # final_training=load_best_trial,
    # compute_shapley_values=compute_shapley_values,
    # shapley_values=shapley_values,
    # gradient_rewards=gradient_rewards,
    metric_list=metric_list,
    # tracked_study=study,
    # tracked_trial=trial,
    min_fit_clients=number_of_clients,
    min_eval_clients=number_of_clients,
    fraction_eval=0.2,
    min_available_clients=number_of_clients,
    initial_parameters=parameters,
    # eval_fn=get_evaluate_function(dataset_factory, model, model_selected, metric_list,
    #                               study, trial, load_best_trial),
    on_fit_config_fn=get_fit_config_func(None),
    on_evaluate_config_fn=get_evaluate_config_func(0, number_of_rounds),
    # model_final_name=model_final_name,
    # result_path="results/" + configuration_id
)

# Start Flower server
fl.server.start_server(
    server_address="localhost:60000",
    config=fl.server.ServerConfig(num_rounds=number_of_rounds),
    strategy=strategy
)
