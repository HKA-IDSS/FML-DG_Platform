import keras
from keras import layers

import flwr
import os
from flower.FedAvgClient import FedAvgClient

import pandas as pd
from flower.Model import MLPModel

"""
Code to define in the file.
"""

input_shape = 30  # Define las dimensiones de entrada (numero de columnas) 
name_dataset = "wine_dataset" # Cambiar el nombre del dataset
client_id = 1 # Cambie el numero a su cliente.

def load_model(learning_rate: float = 0.001):
    model = keras.Sequential(
        [
            keras.Input(shape=(input_shape, )), # No tocar
            layers.Dense(16, activation="relu"), # Puede definir el numero de neuronas y la activacion (relu, tanh)
            layers.Dense(8, activation="relu"), # Puede definir el numero de neuronas y la activacion (relu, tanh)
            layers.Dense(3, activation="softmax") # No tocar
        ]
    )
    # No tocar.
    model.compile(
        "adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model

"""
End of code to define in the file.
"""

model = MLPModel(load_model())


os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
# TODO: If logits are true, than crash
# Function call stack:
# train_function -> assert_greater_equal_Assert_AssertGuard_false_811
# -> train_function -> assert_greater_equal_Assert_AssertGuard_false_811

# The training data is retrieved by using the name of the dataset.
working_directory = os.getcwd() + os.sep + "src" + os.sep + "fl-training-experiments"
directory_for_training_data = working_directory + os.sep + "data" + os.sep + "training_data_preprocessed"
# directory_for_training_data = working_directory + os.sep + "data" + os.sep + "training_data"
# directory_for_training_data_no_preprocessed = working_directory + os.sep + "data" + os.sep + "training_data"
path_to_train_datasets = directory_for_training_data + os.sep + name_dataset
# path_to_train_datasets_no_pro = directory_for_training_data_no_preprocessed + os.sep + name_dataset

X_train = pd.read_csv(path_to_train_datasets + os.sep + "X_train.csv", index_col=0)
y_train = pd.read_csv(path_to_train_datasets + os.sep + "y_train.csv", index_col=0)
X_test = pd.read_csv(path_to_train_datasets + os.sep + "X_test.csv", index_col=0)
y_test = pd.read_csv(path_to_train_datasets + os.sep + "y_test.csv", index_col=0)
# full_dataframe = X.join(y)

metric_list = ["CrossEntropyLoss", "Accuracy"]

# client_strategy = FedAvgClient(model, X_train, X_test, y_train, y_test, client_id, metric_list).to_client()
client_strategy = FedAvgClient(model, X_train, X_test, y_train, y_test,
                               client_number=client_id,
                               metrics=metric_list).to_client()

# Start Flower client
flwr.client.start_client(server_address="10.162.90.200:60000", client=client_strategy)
