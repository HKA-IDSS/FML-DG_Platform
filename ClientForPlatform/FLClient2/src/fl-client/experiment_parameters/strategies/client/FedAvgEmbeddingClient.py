import ast
import os
from logging import INFO
from typing import Tuple, Any, List, Callable, Optional

import flwr as fl
# Define Flower client
import numpy as np
import tensorflow as tf
from flwr.common.logger import log
from numpy import ndarray
from pandas import DataFrame
from sklearn import metrics

from Definitions import ROOT_DIR
from experiment_parameters.model_builder.MobileB2CModels import ContrastiveLossGenerator, \
    embedding_model, contrastive_loss, classification_model

from tensorflow.keras.layers import Input, Softmax, Masking, Embedding, Concatenate, Reshape, BatchNormalization

# from util.Util import evaluate_nn_model, save_data_on_pickle, load_data_from_pickle_file

# def retrieve_gradient_from_dataset(model, X_data, y_data):
#     tensors = tf.convert_to_tensor(X_data.to_numpy())  # Now passing a list of tensors.
#
#     with tf.GradientTape() as tape:
#         predictions = model(tensors)
#         cce = keras.losses.CategoricalCrossentropy()
#         losses = cce(y_data, predictions)
#
#     gradients = tape.gradient(losses, model.trainable_variables)
#
#     return gradients

encoding_size = 64
batch_size_train = 128
batch_count_train = 50

epochs = 5
t_factor = 1000000000  # nano seconds

train_embedding = True

include_validation_data = True  # if any inclusion is required
include_validation_data_scaler = True
include_validation_data_embedding = True
include_validation_data_classifier = True

# auth_interval = 25 * t_factor # equals the size for which an embedding is derived (in seconds)
# overlap_interval = 10 * t_factor # overlap (in seconds) between intervals

mx_size = 71


def calculate_dists(e1, e2):
    #return [np.linalg.norm(e1[a]-e2[a]) for a in range(0, len(e1))]
    return np.sqrt(np.add.reduce(np.square(e1 - e2), 1))


def aggregate_dsts(dsts):
    return np.median(dsts)


class FedAvgClientEmbedding(fl.client.NumPyClient):
    _model: Any
    _model_name: str
    _x_train: DataFrame
    _x_test: DataFrame
    _y_train: DataFrame
    _y_test: DataFrame
    _batch_size: int
    # _shapley_values: ShapleyGTG
    _client_number: int
    _metric_list: list
    # _special_fit_function: Optional[Callable[[DataFrame], DataFrame]] = None
    # Keep initial parameters to initialize SV.
    initial_parameters: List[ndarray] = None

    def __init__(self, model, x_train, x_test, y_train, y_test, client_number, metrics, special_fit_function=None):
        self._model_name = model
        self._x_train = x_train
        self._x_test = x_test
        self._y_train = y_train
        self._y_test = y_test
        # self._batch_size = batch_size
        self._client_number = client_number
        self._metric_list = metrics
        # self._special_fit_function = special_fit_function

        self._gen_train = ContrastiveLossGenerator(self._x_train, batch_size_train, batch_count_train)
        self._model = embedding_model((mx_size, self._gen_train[0][0][0].shape[-1]), encoding_size)

    def get_parameters(self, config):
        return self._model.get_weights()

    # Here, the function belongs to the Tensorflow function fit. So, if implemented for tensorflow, just copy
    # and paste it here.
    def fit(self, parameters, config, global_logits=None) -> Tuple[Any, int, dict]:

        running_loss_t = 0.
        auc_scores_train = []

        for n_epoch in range(epochs):
            for i, ((x_batch_train1, x_batch_train2), y_batch_train) in enumerate(self._gen_train):
                with tf.GradientTape(persistent=True) as tape:
                    emb1 = self._model(x_batch_train1, training=True)
                    emb2 = self._model(x_batch_train2, training=True)
                    loss = contrastive_loss(emb1, emb2, y_batch_train)
                    running_loss_t += tf.squeeze(loss).numpy()

                grads = tape.gradient(loss, self._model.trainable_weights)
                optimizer = tf.keras.optimizers.Adam()
                optimizer.apply_gradients(zip(grads, self._model.trainable_weights))

                # calculate AUC
                e1 = emb1.numpy()
                e2 = emb2.numpy()
                dsts = calculate_dists(e1, e2)

                try:
                    auc = metrics.roc_auc_score(y_batch_train, dsts)
                    auc_scores_train.append(auc)
                except ValueError as e:
                    pass
        log(INFO, f"Total loss for round {str(config['server_round'])}: {running_loss_t}")

        self._gen_train.on_epoch_end()
        return self._model.get_weights(), len(self._x_train), {"client_number": self._client_number}

    def evaluate(self, parameters, config):

        running_losses = {}
        auc_scores = {}
        total_test_loss = 0

        for task in self._x_test.keys():
            flat = [item for sub_list in self._x_test[task] for item in sub_list]

            X1 = np.array([it[0] for it in flat])
            X2 = np.array([it[1] for it in flat])

            emb1 = self._model(X1, training=False)
            emb2 = self._model(X2, training=False)
            dsts = calculate_dists(emb1.numpy(), emb2.numpy())

            y_pred = []
            y_true = self._y_test[task]
            y_embs = []

            pointer = 0
            label_pointer = 0

            for sess in self._x_test[task]:
                sesslen = len(sess)
                sessdsts = dsts[pointer:pointer + sesslen]
                pointer += sesslen
                y_pred.append(aggregate_dsts(sessdsts))

                ilabel = y_true[label_pointer]
                y_embs.extend([ilabel for z in range(0, sesslen)])
                label_pointer += 1
                # total_test_loss += contrastive_loss(emb1, emb2, self._y_test[task])

            y_pred = np.array(y_pred)

            running_losses[task] = contrastive_loss(emb1.numpy(), emb2.numpy(), np.array(y_embs)).numpy().item()

            try:
                auc = metrics.roc_auc_score(y_true, y_pred)
                auc_scores[task] = auc.item()
            except ValueError as e:
                pass

        total_auc = 0
        total_test_loss = 0
        metric_results = {}

        for task in auc_scores.keys():
            total_auc += auc_scores[task]
            total_test_loss += running_losses[task]

        # self._model.set_weights(parameters)
        # round_result = evaluate_nn_model(self._x_test, self._y_test, self._model, parameters, self._metric_list)
        # flower_metrics = self._model.evaluate(self._x_test, self._y_test, verbose=0)
        #
        # metric_results = round_result.return_flower_dict()
        metric_results["AUC"] = total_auc / (len(auc_scores.keys()))
        return total_test_loss, len(self._x_test), metric_results
