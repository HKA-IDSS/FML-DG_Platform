import ast
import os
from logging import INFO
from typing import Tuple, Any, List

import flwr as fl
# Define Flower client
import keras
import numpy as np
from flwr.common.logger import log
from numpy import ndarray
from pandas import DataFrame
from .Evaluator import evaluator
from .Model import KerasModel

class FedAvgClient(fl.client.NumPyClient):
    _model: KerasModel
    # _model_name: str
    _x_train: DataFrame
    _x_test: DataFrame
    _y_train: DataFrame
    _y_test: DataFrame
    _batch_size: int
    # _shapley_values: ShapleyGTG
    _client_number: int
    _metric_list: list
    # _last_round_result = DictOfMetrics

    # Keep initial parameters to initialize SV.
    initial_parameters: List[ndarray] = None

    def __init__(self, model, x_train, x_test, y_train, y_test, client_number, metrics):
        self._model = model
        self._x_train = x_train
        self._x_test = x_test
        self._y_train = y_train
        self._y_test = y_test
        # self._batch_size = batch_size
        self._client_number = client_number
        self._metric_list = metrics

    def get_parameters(self, config):
        return self._model.get_model().get_weights()

    # Here, the function belongs to the Tensorflow function fit. So, if implemented for tensorflow, just copy
    # and paste it here.
    def fit(self, parameters, config, global_logits=None) -> Tuple[Any, int, dict]:
        if config["server_round"] == 1:
            log(INFO, "Config: {}".format(config))
            # self._model
            self._batch_size = 32

        if self.initial_parameters is not None:
            self.initial_parameters = parameters
            self._model.set_model(self.initial_parameters)

        # if config["server_round"] == 1:
        #     self._model.set_model(parameters)

        labels, counts = np.unique(np.argmax(np.asarray(self._y_train), axis=1), return_counts=True)
        label_names = self._y_train.columns
        metrics = {"client_number": self._client_number}
        for label, count in zip(labels, counts):
            metrics["Label " + str(label_names[label])] = int(count)

        # if global_logits is not None:
        # log(INFO, "Labels: {}".format(metrics))

        my_callbacks = [
            keras.callbacks.EarlyStopping(patience=2),
        ]

        self._model.fit(self._x_train,
                        self._y_train,
                        epochs=1,
                        batch_size=self._batch_size)

        return self._model.get_model().get_weights(), len(self._x_train), metrics

    def evaluate(self, parameters, config):
        self._model.set_model(parameters)
        round_result = evaluator(self._x_test, self._y_test, self._model, self._metric_list)
        metric_results = round_result.return_flower_dict_as_str()
        loss = round_result.get_value_of_metric("CrossEntropyLoss")

        log(INFO, f"Round result: {round_result.return_flower_dict_as_str()}")

        return loss, len(self._x_test), metric_results
