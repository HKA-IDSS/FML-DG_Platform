import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder


def one_hot_encode_labels(y):
    y_reshaped = np.reshape(y.values, (-1, 1))
    encoder = OneHotEncoder().fit(y_reshaped)
    y_encoded = encoder.transform(y_reshaped)
    labels = encoder.get_feature_names_out()
    y_one_hot_encoded = pd.DataFrame(y_encoded.toarray(), index=y.index, columns=labels)
    return y_one_hot_encoded, labels


def one_hot_encode_column(X_column, categories):
    encoded_dataframe = pd.DataFrame()
    X_column = X_column.str.strip()
    X_column = X_column.str.lower()
    for category in categories:
        category = category.strip()
        category = category.lower()
        encoded_dataframe[category] = X_column == category
        encoded_dataframe[category] = encoded_dataframe[category].astype(int)
    # encoded_dataframe[X.loc[:]] = 1
    return encoded_dataframe


def scale_column(X_column, min_value, max_value):
    X_std = (X_column - min_value) / (max_value - min_value)
    # X_scaled = X_std * (max_value - min_value) + min_value
    return X_std
