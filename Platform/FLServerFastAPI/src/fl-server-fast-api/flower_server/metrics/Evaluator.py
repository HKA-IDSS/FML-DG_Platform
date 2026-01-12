from logging import INFO
from typing import List, Union
import numpy as np
import xgboost
from flwr.common import log
from pandas import DataFrame
from sklearn.metrics import log_loss, accuracy_score, matthews_corrcoef, f1_score
from xgboost import DMatrix

from experiment_parameters import TrainerFactory
from experiment_parameters.model_builder.Model import Model, XGBoostModel
from experiment_parameters.model_builder.ModelBuilder import Director, get_training_configuration
from metrics.Metrics import DictOfMetrics, Accuracy, CrossEntropyLoss, SVCompatibleF1Score, \
    SVCompatibleMatthewsCorrelationCoefficient, return_default_dict_of_metrics, F1ScoreMacro, F1ScoreMicro
from util import OptunaConnection


def return_labels(y_true_argmaxed, labels):
    # y_true_argmaxed = np.reshape(y_true_argmaxed, newshape=(-1, 1))
    # print(np.apply_along_axis(lambda x: print(x), 0, y_true_argmaxed))
    return [labels[selected_class] for selected_class in y_true_argmaxed]


def cross_entropy_loss(y_test, y_pred_proba, labels) -> CrossEntropyLoss:
    # log(INFO, "CE Loss")
    ground_truth_np = return_labels(np.argmax(y_test, axis=1), labels)
    return CrossEntropyLoss(log_loss(ground_truth_np, y_pred_proba, labels=labels))


def accuracy(y_test, y_pred, labels) -> Accuracy:
    # log(INFO, "Accuracy")
    y_pred = np.argmax(y_pred, axis=1)
    ground_truth_np = np.argmax(y_test, axis=1)
    return Accuracy(accuracy_score(ground_truth_np, y_pred))


def f1_score_local(y_test, y_pred_proba, labels) -> SVCompatibleF1Score:
    # log(INFO, "F1 Score")
    ground_truth_np = return_labels(np.argmax(y_test, axis=1), labels)
    predictions_np = return_labels(np.argmax(y_pred_proba, axis=1), labels)
    # print(f1_score(ground_truth_np, predictions_np, labels=labels, average=None, zero_division=0))
    return SVCompatibleF1Score(f1_score(ground_truth_np, predictions_np, labels=labels, average=None, zero_division=0))


def f1_score_micro(y_test, y_pred_proba, labels) -> F1ScoreMicro:
    # log(INFO, "F1 Score")
    ground_truth_np = return_labels(np.argmax(y_test, axis=1), labels)
    predictions_np = return_labels(np.argmax(y_pred_proba, axis=1), labels)
    # print(f1_score(ground_truth_np, predictions_np, labels=labels, average=None, zero_division=0))
    return F1ScoreMicro(f1_score(ground_truth_np, predictions_np, labels=labels, average="micro", zero_division=0))


def f1_score_macro(y_test, y_pred_proba, labels) -> F1ScoreMacro:
    # log(INFO, "F1 Score")
    ground_truth_np = return_labels(np.argmax(y_test, axis=1), labels)
    predictions_np = return_labels(np.argmax(y_pred_proba, axis=1), labels)
    # print(f1_score(ground_truth_np, predictions_np, labels=labels, average=None, zero_division=0))
    return F1ScoreMacro(f1_score(ground_truth_np, predictions_np, labels=labels, average="macro", zero_division=0))


def mcc(y_test, y_pred, labels) -> SVCompatibleMatthewsCorrelationCoefficient:
    # log(INFO, "MCC")
    y_pred = np.argmax(y_pred, axis=1)
    ground_truth_np = np.argmax(y_test, axis=1)
    return SVCompatibleMatthewsCorrelationCoefficient(matthews_corrcoef(ground_truth_np, y_pred))


metric_function_dict = {
    "CrossEntropyLoss": cross_entropy_loss,
    "Accuracy": accuracy,
    # "F1Score": f1_score_local,
    "F1ScoreMacro": f1_score_macro,
    "F1ScoreMicro": f1_score_micro,
    "MCC": mcc
}


def evaluator(x_test: Union[DataFrame, DMatrix], y_test, model: Model, metric_list: List[str]):
    # log(INFO, "Evaluating")
    metric_dict = DictOfMetrics()
    # model.set_model(weights)
    # y_pred_proba = model.predict_proba(x_test)
    if type(model) is XGBoostModel:
        # x_test_matrix = DMatrix(x_test)
        y_pred_proba = model.predict_proba(x_test)
    else:
        y_pred_proba = model.predict_proba(x_test)

    for metric in metric_list:
        # TODO: Replace in the dockerize version with the input parameters
        metric_dict.add_metric(metric_function_dict[metric](y_test, y_pred_proba, labels=list(y_test.columns)))

    return metric_dict


#
# def evaluate_nn_model(x_test, y_test, model: TFModel, weights, metric_list) -> DictOfMetrics:
#     # Parameter to be returned.
#     metric_dict = DictOfMetrics()
#     # Update model with the latest parameters
#     # log(INFO, f"Weights incoming: {len(weights)}")
#     # log(INFO, f"Model len weights: {model}")
#     model.set_model(weights)
#
#     # TFModel evaluate will return the metrics used on compile,
#     # on Dataset.
#     labels = list(y_test.columns)
#     y_pred = model.predict(x_test, verbose=0)
#
#     # Default metrics.
#     # loss = metrics[0]
#     # accuracy = metrics[1]
#     metric_dict.add_metric(CrossEntropyLoss(y_pred))
#     metric_dict.add_metric(Accuracy(accuracy_score(np.argmax(y_pred, axis=1))))
#
#     if "F1Score" in metric_list:
#         def return_label(predicted):
#             return labels[predicted]
#
#         vectorized_function = np.vectorize(return_label)
#         ground_truth_np = vectorized_function(np.argmax(y_test, axis=1))
#         predictions_np = vectorized_function(np.argmax(y_pred, axis=1))
#         metric_dict.add_metric(SVCompatibleF1Score(f1_score(ground_truth_np,
#                                                             predictions_np,
#                                                             labels=labels,
#                                                             average=None,
#                                                             zero_division=0)))
#     if "MCC" in metric_list:
#         metric_dict.add_metric(SVCompatibleMatthewsCorrelationCoefficient(matthews_corrcoef(y_test, y_pred)))
#
#     return metric_dict
#
#
# """
# For now, this function is only prepared for xgboost.
# """
#
#
# def evaluate_tree_model(x_test, y_test, xgb_model_parameters, metric_list):
#     metric_dict = DictOfMetrics()
#     xgb_model = xgb.Booster()
#     xgb_model.load_model(bytearray(xgb_model_parameters))
#     y_pred = xgb_model.predict(xgb.DMatrix(x_test))
#     log(INFO, f"Predictions: {y_pred}")
#
#     if y_test.shape[1] == 2:
#         metric_dict.add_metric(CrossEntropyLoss(mean_absolute_error(np.argmax(y_test, axis=1),
#                                                                     y_pred)))
#
#         vectorized_function = np.vectorize(lambda pred: 1 if pred >= 0.5 else 0)
#         y_pred = vectorized_function(y_pred)
#         metric_dict.add_metric(Accuracy(accuracy_score(np.argmax(y_test, axis=1),
#                                                        y_pred)))
#
#         if "F1Score" in metric_list:
#             metric_dict.add_metric(SVCompatibleF1Score(f1_score(np.argmax(y_test, axis=1),
#                                                                 y_pred,
#                                                                 average=None,
#                                                                 zero_division=0)))
#
#     else:
#         metric_dict.add_metric(CrossEntropyLoss(mean_absolute_error(np.argmax(y_test, axis=1), y_pred)))
#
#         metric_dict.add_metric(Accuracy(accuracy_score(np.argmax(y_test, axis=1),
#                                                        y_pred)))
#
#         if "F1Score" in metric_list:
#             metric_dict.add_metric(SVCompatibleF1Score(f1_score(np.argmax(y_test, axis=1),
#                                                                 y_pred,
#                                                                 average=None,
#                                                                 zero_division=0)))
#     # if "MCC" in metric_list:
#     #     metric_dict.add_metric(SVCompatibleMatthewsCorrelationCoefficient(matthews_corrcoef(y_test, y_pred)))
#
#     return metric_dict

if __name__ == "__main__":
    x_train, y_train = TrainerFactory.dataset_model_dictionary["adult"]().get_dataset().get_training_data()
    x_test, y_test = TrainerFactory.dataset_model_dictionary["adult"]().get_dataset().get_test_data()
    dmatrix = xgboost.DMatrix(x_train, label=np.argmax(y_train, axis=1))
    dmatrix_test = xgboost.DMatrix(x_test, label=np.argmax(y_test, axis=1))
    director = Director()
    study = OptunaConnection.load_study("xgboost_adult")
    trial = None  # Quickfix. Not so nicely programmed.
    trial_with_highest_accuracy = study.best_trial
    parameters_dict = get_training_configuration(trial_with_highest_accuracy, "xgboost")
    xgboost_hyperparameters = director.create_xgboost(input_parameters=x_train.shape[1],
                                                      num_classes=y_train.shape[1],
                                                      parameters=parameters_dict)
    bst = xgboost.train(xgboost_hyperparameters,
                        dmatrix,
                        evals=[(dmatrix_test, "validate"), (dmatrix, "train")],
                        num_boost_round=100)
    model = XGBoostModel(bst)
    metric_list = ["CrossEntropyLoss", "Accuracy", "F1Score", "MCC", "F1ScoreMacro", "F1ScoreMicro"]
    # #
    # # # model = keras.saving.load_model("data" +
    # # #                                 os.sep + "global_model" +
    # # #                                 os.sep + "FedAvg_wine_dirichlet_100_mlp.keras")
    metrics = evaluator(x_test, y_test, model, metric_list)
    print(metrics)
    # metrics = return_default_dict_of_metrics(metric_list, 3)
    # flower_metrics = metrics.return_flower_dict_as_str()
    # flower_metrics["SV_test"] = 0
    # print(flower_metrics)
    # print([flower_metric for flower_metric in flower_metrics if flower_metric in metric_list])
    # print([flower_metric for flower_metric in flower_metrics if "SV" in flower_metric])
