import os
from typing import Optional

import pandas as pd


def load_data(dataset_name, client_number=None):
    # The training data is retrieved by using the name of the dataset.
    working_directory = os.getcwd()
    directory_for_training_data = working_directory + os.sep + "data" + os.sep + "training_data_preprocessed"
    path_to_train_datasets = directory_for_training_data + os.sep + dataset_name

    y_train = None

    # TODO: Remove the client number
    X_train = pd.read_csv(path_to_train_datasets + os.sep + "client_" + client_number + "_X_training.csv", index_col=0)
    if os.path.isfile(path_to_train_datasets + os.sep + "client_" + client_number + "_y_training.csv"):
        y_train = pd.read_csv(path_to_train_datasets + os.sep + "client_" + client_number + "_y_training.csv",
                              index_col=0)
    X_test = pd.read_csv(path_to_train_datasets + os.sep + "client_" + client_number + "_X_test.csv", index_col=0)
    y_test = pd.read_csv(path_to_train_datasets + os.sep + "client_" + client_number + "_y_test.csv", index_col=0)

    return X_train, y_train, X_test, y_test


class DataLoader:
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: Optional[pd.DataFrame]
    y_test: Optional[pd.DataFrame]

    def __init__(self, X_train, X_test, y_train = None, y_test = None, need_for_sample=None):
        self.X_train = X_train
        self.X_test = X_test
        self.y_train = y_train
        self.y_test = y_test

    def get_training_data(self):
        return self.X_train, self.y_train

    def get_test_data(self):
        return self.X_train, self.y_train


# class CustomDataLoader(DataLoader):
#
#     def __init__(self, X_train, X_test, y_train = None, y_test = None):
#         super().__init__(X_train, X_test, y_train, y_test)
#
#
#
#     def get_training_data(self):
#         self
