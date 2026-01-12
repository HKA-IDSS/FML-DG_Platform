import ast
import math
import os
from functools import partial, reduce
from logging import WARNING, INFO
from typing import Callable, Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
from flwr.common import Parameters, Scalar, FitRes, NDArray, parameters_to_ndarrays, \
    ndarrays_to_parameters, EvaluateIns, EvaluateRes, FitIns
from flwr.common.logger import log
from flwr.server.client_manager import ClientManager
from flwr.server.client_proxy import ClientProxy
from flwr.server.strategy import FedAvg
from flwr.server.strategy.aggregate import aggregate, weighted_loss_avg

from Definitions import ROOT_DIR
from metrics.GradientRewards import GradientRewards
from metrics.Metrics import return_default_dict_of_metrics
from metrics.ResultManager import FlowerMetricManager, SVCompatibleFlowerMetricManager

DEPRECATION_WARNING = """
DEPRECATION WARNING: deprecated `eval_fn` return format

    loss, accuracy

move to

    loss, {"accuracy": accuracy}

instead. Note that compatibility with the deprecated return format will be
removed in a future release.
"""

DEPRECATION_WARNING_INITIAL_PARAMETERS = """
DEPRECATION WARNING: deprecated initial parameter type

    flwr.common.Weights (i.e., List[np.ndarray])

will be removed in a future update, move to

    flwr.common.Parameters

instead. Use

    parameters = flwr.common.weights_to_parameters(weights)

to easily transform `Weights` to `Parameters`.
"""

WARNING_MIN_AVAILABLE_CLIENTS_TOO_LOW = """
Setting `min_available_clients` lower than `min_fit_clients` or
`min_eval_clients` can cause the server to fail when there are too few clients
connected to the server. `min_available_clients` must be set to a value larger
than or equal to the values of `min_fit_clients` and `min_eval_clients`.
"""


def save_data_on_joblib(path_file, data):
    # file = open(path_file, 'wb')
    joblib.dump(data, path_file)
    # file.close()


def save_model_with_tensorflow(path_file, model):
    model.save(path_file + ".keras")


class FedAvgEmbedding(FedAvg):
    """Configurable fedavg strategy implementation."""
    _gradient_rewards: GradientRewards
    _max_round: int
    _compute_shapley_values: bool
    _model_final_name: str
    _id_and_client_number: List[tuple]
    _dataset_metrics: FlowerMetricManager | SVCompatibleFlowerMetricManager

    # _former

    # pylint: disable=too-many-arguments,too-many-instance-attributes
    def __init__(
            self,
            max_round,
            # dataset_factory,
            x_test,
            y_test,
            model,
            final_training,
            # shapley_values,
            # gradient_rewards,
            metric_list,
            model_final_name,
            # compute_shapley_values,
            result_path,
            fraction_fit: float = 0.1,
            fraction_eval: float = 0.1,
            min_fit_clients: int = 2,
            min_eval_clients: int = 2,
            min_available_clients: int = 2,
            eval_fn: Optional[
                Callable[[NDArray], Optional[Tuple[float, Dict[str, Scalar]]]]
            ] = None,
            on_fit_config_fn: Optional[Callable[[int], Dict[str, Scalar]]] = None,
            on_evaluate_config_fn: Optional[Callable[[int], Dict[str, Scalar]]] = None,
            accept_failures: bool = True,
            initial_parameters: Optional[Parameters] = None,
    ) -> None:

        super().__init__()

        if (
                min_fit_clients > min_available_clients
                or min_eval_clients > min_available_clients
        ):
            log(WARNING, WARNING_MIN_AVAILABLE_CLIENTS_TOO_LOW)

        self.fraction_fit = fraction_fit
        self.fraction_eval = fraction_eval
        self.min_fit_clients = min_fit_clients
        self.min_eval_clients = min_eval_clients
        self.min_available_clients = min_available_clients
        self.evaluate_fn = eval_fn
        self.on_fit_config_fn = on_fit_config_fn
        self.on_evaluate_config_fn = on_evaluate_config_fn
        self.accept_failures = accept_failures
        self.initial_parameters = initial_parameters

        # Added attributes
        # self._evaluation_dataset = dataset_factory.get_dataset()
        self._model = model
        self._final_training = final_training
        # self._shapley_values = shapley_values
        # self._gradient_rewards = gradient_rewards
        self._metric_list = metric_list
        self._clients_weights = None
        self._max_round = max_round
        # self._compute_shapley_values = compute_shapley_values
        self._model_final_name = model_final_name
        self._result_path = result_path

        # Information for evaluation purposes.
        self._total_test_samples = None
        self._samples_per_class = None
        self._x_test = x_test
        self._y_test = y_test

    def initialize_parameters(
            self, client_manager: ClientManager
    ) -> Tuple[Optional[Parameters]]:
        """Initialize global model parameters."""
        initial_parameters = self.initial_parameters
        # self.initial_parameters  # Keeping initial parameters in memory
        return initial_parameters

    def evaluate(
            self, server_round: int, parameters: Parameters
    ) -> Optional[Tuple[float, Dict[str, Scalar]]]:
        """Evaluate model parameters using an evaluation function."""
        if self.evaluate_fn is None:
            log(INFO, "No evaluation function provided")
            # No evaluation function provided
            return None
        parameters_ndarrays = parameters_to_ndarrays(parameters)
        eval_res = self.evaluate_fn(server_round, parameters_ndarrays, {})
        if eval_res is None:
            return None

        loss, metrics = eval_res

        if server_round != 0 and self._final_training == 1:
            for metric, value in metrics.items():
                self._dataset_metrics.add_result(metric, "Global", server_round, value)

        if server_round == self._max_round and self._final_training == 1:
            self._dataset_metrics.save_dataframes_as_csv(self._result_path)

        return loss, metrics

    def configure_fit(
            self, server_round: int, parameters: Parameters, client_manager: ClientManager
    ) -> List[Tuple[ClientProxy, FitIns]]:
        """Configure the next round of training."""
        config = {"server_round": server_round}
        if self.on_fit_config_fn is not None:
            # Custom fit config function provided
            config = self.on_fit_config_fn(server_round)
        fit_ins = FitIns(parameters, config)

        # if self._compute_shapley_values:
        #     config["compute_shapley_values"] = 1
        # else:
        #     config["compute_shapley_values"] = 0

        # Sample clients
        sample_size, min_num_clients = self.num_fit_clients(
            client_manager.num_available()
        )
        clients = client_manager.sample(
            num_clients=sample_size, min_num_clients=min_num_clients
        )

        # Return client/config pairs
        return [(client, fit_ins) for client in clients]

    def aggregate_fit(
            self,
            server_round: int,
            results: List[Tuple[ClientProxy, FitRes]],
            failures: List[Union[Tuple[ClientProxy, FitRes], BaseException]],
    ) -> Tuple[Optional[Parameters], Dict[str, Scalar]]:
        """
        Aggregate fit results using weighted average.

        Args:
            rnd (int): _description_
            results (List[Tuple[ClientProxy, FitRes]]): _description_
            failures (List[BaseException]): _description_

        Returns:
            Tuple[Optional[Parameters], Dict[str, Scalar]]: _description_
        """
        if not results:
            return None, {}
        # Do not aggregate if there are failures and failures are not accepted
        if not self.accept_failures and failures:
            return None, {}
        # Convert results
        client_weights = dict()
        # self._id_and_client_number: list = sorted([(client.cid, fit_res.metrics["client_number"])
        #                                            for client, fit_res in results])
        self._id_and_client_number: dict = {client.cid: fit_res.metrics["client_number"] for client, fit_res in results}
        # clients_data_size_dict: dict = {client.cid: fit_res.num_examples for client, fit_res in results}
        # clients_list: list = sorted(list(clients_data_size_dict.keys()))
        # for client, fit_res in results:
        #     client_weights[client.cid] = (parameters_to_ndarrays(fit_res.parameters), fit_res.num_examples)

        if server_round == 1 and self._final_training == 1:
            for client, number_assigned in self._id_and_client_number.items():
                log(INFO, "Clients_id: {} and number assigned: {}".format(client, number_assigned))

            # x_test, y_test = self._evaluation_dataset.get_test_data()
            self._dataset_metrics = FlowerMetricManager(
                metric_list=self._metric_list,
                client_list=list(self._id_and_client_number.values()),
                number_of_rounds=self._max_round,
                classes=[0, 1]
            )

        # We store here the weights, to then pass them to the clients.
        self._clients_weights = client_weights
        weights_results = [
            (parameters_to_ndarrays(fit_res.parameters), fit_res.num_examples)
            for client, fit_res in results
        ]
        new_model = aggregate(weights_results)

        if server_round == self._max_round:
            # Saving model in pickle.
            self._model.set_weights(new_model)
            model_to_save = self._model
            save_model_with_tensorflow(ROOT_DIR +
                                       os.sep + "data" +
                                       os.sep + "global_model" +
                                       os.sep + self._model_final_name,
                                       model_to_save)

        new_model_to_parameters = ndarrays_to_parameters(new_model)

        return new_model_to_parameters, {}

    def configure_evaluate(
            self, server_round: int, parameters: Parameters, client_manager: ClientManager
    ) -> List[Tuple[ClientProxy, EvaluateIns]]:
        """Configure the next local_round of evaluation."""
        # Do not configure federated evaluation if fraction eval is 0.
        if self.fraction_evaluate == 0.0:
            return []

        # Parameters and config
        config = {}
        if self.on_evaluate_config_fn is not None:
            # Custom evaluation config function provided
            # config = self.on_evaluate_config_fn(server_round, self._clients_weights)
            config = self.on_evaluate_config_fn(server_round)

            if server_round == self._max_round:
                config["last_round"] = 1
            else:
                config["last_round"] = 0
        evaluate_ins = EvaluateIns(parameters, config)

        # Sample clients
        sample_size, min_num_clients = self.num_evaluation_clients(
            client_manager.num_available()
        )
        clients = client_manager.sample(
            num_clients=sample_size, min_num_clients=min_num_clients
        )

        # Return client/config pairs
        return [(client, evaluate_ins) for client in clients]

    def normalize_metric(self, metric, portion_of_samples):
        if type(metric) is list:
            return [value * portion_of_samples for value in metric]
        elif type(metric) is float or type(metric) is int:
            return metric * portion_of_samples

    def sum_metrics(self, first_value, second_value):
        if type(first_value) is list:
            return [x + y for x, y in zip(first_value, second_value)]
        elif type(first_value) is float or type(first_value) is int:
            return first_value + second_value

    def aggregate_evaluate(
            self,
            server_round: int,
            results: List[Tuple[ClientProxy, EvaluateRes]],
            failures: List[Union[Tuple[ClientProxy, EvaluateRes], BaseException]],
    ) -> Tuple[Optional[float], Dict[str, Scalar]]:
        """Aggregate evaluation losses using weighted average."""
        if not results:
            return None, {}
        # Do not aggregate if there are failures and failures are not accepted
        if not self.accept_failures and failures:
            return None, {}

        # if os.path.exists(ROOT_DIR + os.sep + "data" + os.sep + "pickled_information" + os.sep + "model.pkl"):
        #     os.remove(ROOT_DIR + os.sep + "data" + os.sep + "pickled_information" + os.sep + "model.pkl")
        #
        # # Aggregate loss
        # loss_aggregated = weighted_loss_avg(
        #     [
        #         (evaluate_res.num_examples, evaluate_res.loss)
        #         for _, evaluate_res in results
        #     ]
        # )
        #
        # # metrics_aggregated = {}
        # eval_metrics = {self._id_and_client_number[client.cid]: (res.num_examples, res.metrics)
        #                 for client, res in results}
        # total_of_samples = 0
        # total_of_samples_per_class = {}
        # for client, metrics in eval_metrics.items():
        #     # metrics[0] = ast.literal_eval(metrics[0])
        #     total_of_samples += metrics[0]
        #     dictionary_of_metrics = metrics[1]
        #     for metric in dictionary_of_metrics:
        #         dictionary_of_metrics[metric] = ast.literal_eval(dictionary_of_metrics[metric])
        #
        # normalized_metrics = []
        # for client, metrics in eval_metrics.items():
        #     partial_function = partial(self.normalize_metric, portion_of_samples=metrics[0] / total_of_samples)
        #     log(INFO, f"Client number {client}")
        #     log(INFO, f"Metrics: {metrics[1]}")
        #
        #     if self._final_training == 1:
        #         for metric, value in metrics[1].items():
        #             self._dataset_metrics.add_result(metric, client, server_round, value)
        #
        #     aggregated_metrics = {metric: partial_function(value) for metric, value in metrics[1].items()}
        #     normalized_metrics.append(aggregated_metrics)
        #
        # metrics_aggregated = reduce(lambda dict1, dict2: {key: self.sum_metrics(dict1[key], dict2[key])
        #                                                   for key in dict1},
        #                             normalized_metrics)
        # log(INFO, f"Metrics Aggregated: {metrics_aggregated}")
        # if self._final_training == 1:
        #     for metric, value in metrics_aggregated.items():
        #         self._dataset_metrics.add_result(metric, "Aggregated", server_round, value)
        # # # Aggregate custom metrics if aggregation fn was provided
        # #
        # # if self.evaluate_metrics_aggregation_fn:
        # #     eval_metrics = [(res.num_examples, res.metrics) for _, res in results]
        # #     metrics_aggregated = self.evaluate_metrics_aggregation_fn(eval_metrics)
        # # elif server_round == 1:  # Only log this warning once
        # #     log(WARNING, "No evaluate_metrics_aggregation_fn provided")

        return 0, {'0': 0}
