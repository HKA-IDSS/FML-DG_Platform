import ast
from logging import INFO
from sys import argv

import flwr as fl
from flwr.common.logger import log

from experiment_parameters.TrainerFactory import strategies_dictionary
from experiment_parameters.model_builder.Model import XGBoostModel
from experiment_parameters.model_builder.ModelBuilder import get_training_configuration, Director
from util import OptunaConnection

connection_port = argv[1]
strategy_selected = argv[2]
possible_outputs = ast.literal_eval(argv[3])
model_selected = argv[4]
hyperparameter_space = ast.literal_eval(argv[5])
input_dim = int(argv[6])
output_dim = int(argv[7])
number_of_clients = int(argv[8])
log(INFO, f"Min number of clients: {number_of_clients}")
number_of_rounds = int(argv[9])
metric_list = argv[10].split("-")
model_final_name = argv[11]
load_best_trial = int(argv[12])
compute_shapley_values = int(argv[13])
configuration_id = argv[14]

study = OptunaConnection.load_study(model_final_name)

if load_best_trial == 0:
    trial = study.ask()
    parameters_dict = get_training_configuration(trial, model_selected, hyperparameter_space)

elif load_best_trial == 1:
    trial = None  # Quickfix. Not so nicely programmed.
    trial_with_highest_accuracy = study.best_trial
    parameters_dict = get_training_configuration(trial_with_highest_accuracy, model_selected, hyperparameter_space)
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
        if server_round == 1:
            config.update(parameters_dict)
            log(INFO, "Updating config: {}".format(parameters_dict))
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
logits = False
if strategy_selected in ["FedKD", "FedDKD"]:
    logits = True

# log(INFO, "Logits: {}".format(logits))
# This is the model. For retrieving the model class (type of instance TFModel)
# from the file Model.py.


director = Director()
if model_selected != "xgboost":
    # model = factory_return_model(dataset_factory, model_selected, parameters_dict)
    model = director.create_mlp(input_dim, output_dim, parameters_dict)

    # Flower work with NDArrays, which is what you get when you use get_weights op.
    weights = model.get_model().get_weights()

    parameters = fl.common.ndarrays_to_parameters(weights)

    # shapley_values = ShapleyValuesNN(X_test, y_test, number_of_rounds, metric_list)
    # gradient_rewards = GradientRewards(number_of_clients)

else:
    model = XGBoostModel()
    parameters = None

    xgboost_training_params = director.create_xgboost(input_dim, output_dim, parameters_dict)
    #
    # model.fit(xgboost_training_params,
    #           x_train=X_train,
    #           x_test=X_test,
    #           y_train=y_train,
    #           y_test=y_test,
    #           num_local_rounds=1)
    #
    # shapley_values = ShapleyValuesDT(X_test, y_test, number_of_rounds, metric_list)

#
# # The `evaluate` function will be called after every round
# # It needs to be positioned here, as it needs to have the model defined before.
# def get_evaluate_function(dataset_factory, model, model_selected, metric_list, study, trial, load_best_trial):
#     def evaluate(
#             server_round: int, parameters: Optional[Parameters | bytes], config: Dict[str, Scalar]
#     ) -> Optional[Tuple[float, Dict[str, Scalar]]]:
#         log(INFO, "Server round in evaluate: {}".format(server_round))
#         log(INFO, "Metric list: {}".format(metric_list))
#         x_test, y_test = dataset_factory.get_dataset().get_test_data()
#         if model_selected == "xgboost" and server_round == 0:
#             evaluation_results = return_default_dict_of_metrics(metric_list, y_test.shape[1])
#         else:
#             model.set_model(parameters)
#             evaluation_results = evaluator(x_test, y_test, model, metric_list)
#             # evaluation_results = evaluate_tree_model(x_test, y_test, parameters, metric_list)
#
#         # all_results = {"Accuracy": evaluation_results.get_value_of_metric("Accuracy")}
#         log(INFO, "Loss of global model: {}".format(evaluation_results.get_value_of_metric("CrossEntropyLoss")))
#         log(INFO, "Accuracy of global model: {}".format(evaluation_results.get_value_of_metric("Accuracy")))
#         print("Loss of global model: {}".format(evaluation_results.get_value_of_metric("CrossEntropyLoss")))
#         print("Accuracy of global model: {}".format(evaluation_results.get_value_of_metric("Accuracy")))
#         if "F1Score" in metric_list:
#             log(INFO, "F1Score of global model: {}".format(evaluation_results.get_value_of_metric("F1Score")))
#             print("F1Score of global model: {}".format(evaluation_results.get_value_of_metric("F1Score")))
#             # all_results["F1Score"] = evaluation_results.get_value_of_metric("F1Score")
#         if "MCC" in metric_list:
#             log(INFO, "MCC of global model: {}".format(evaluation_results.get_value_of_metric("MCC")))
#             print("MCC of global model: {}".format(evaluation_results.get_value_of_metric("MCC")))
#             # all_results["MCC"] = evaluation_results.get_value_of_metric("MCC")
#
        # if server_round == 20 and load_best_trial == 0:
        #     study.tell(trial, evaluation_results.get_value_of_metric("CrossEntropyLoss"))
#                        [evaluation_results.get_value_of_metric("CrossEntropyLoss"),
#                         evaluation_results.get_value_of_metric("Accuracy")])
#
#         return evaluation_results.get_value_of_metric("CrossEntropyLoss"), evaluation_results.return_flower_dict()
#
#     return evaluate


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


strategy_type = strategies_dictionary[strategy_selected]().create_strategy()
strategy = strategy_type(
    # ... other fedavg arguments
    max_round=number_of_rounds,
    possible_outputs=possible_outputs,
    model=model,
    final_training=load_best_trial,
    compute_shapley_values=compute_shapley_values,
    # shapley_values=shapley_values,
    # gradient_rewards=gradient_rewards,
    metric_list=metric_list,
    tracked_study=study,
    tracked_trial=trial,
    min_fit_clients=number_of_clients,
    min_eval_clients=number_of_clients,
    fraction_eval=0.2,
    min_available_clients=number_of_clients,
    initial_parameters=parameters,
    # eval_fn=get_evaluate_function(dataset_factory, model, model_selected, metric_list,
    #                               study, trial, load_best_trial),
    on_fit_config_fn=get_fit_config_func(parameters_dict),
    on_evaluate_config_fn=get_evaluate_config_func(compute_shapley_values, number_of_rounds),
    model_final_name=model_final_name,
    result_path="results/" + configuration_id
)

# Start Flower server
fl.server.start_server(
    server_address="0.0.0.0:" + connection_port,
    config=fl.server.ServerConfig(num_rounds=number_of_rounds),
    strategy=strategy
)
