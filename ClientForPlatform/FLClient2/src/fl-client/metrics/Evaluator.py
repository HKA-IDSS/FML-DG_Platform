from typing import List, Union
import numpy as np
from pandas import DataFrame
from sklearn.metrics import log_loss, accuracy_score, matthews_corrcoef, f1_score
from xgboost import DMatrix

from experiment_parameters import TrainerFactory
from experiment_parameters.model_builder.Model import Model, XGBoostModel
from experiment_parameters.model_builder.ModelBuilder import Director
from metrics.Metrics import DictOfMetrics, Accuracy, CrossEntropyLoss, SVCompatibleF1Score, \
    SVCompatibleMatthewsCorrelationCoefficient, return_default_dict_of_metrics, F1ScoreMacro, F1ScoreMicro


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
    "F1Score": f1_score_local,
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

