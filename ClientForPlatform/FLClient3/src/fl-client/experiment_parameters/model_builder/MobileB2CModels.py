import random

import keras
import tensorflow as tf
from tensorflow.keras import ops
import numpy as np

## Code for Davids part.
from tensorflow.keras import regularizers
from tensorflow.keras.layers import Activation, Embedding, ReLU
from tensorflow.keras.regularizers import l2

# from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
from tensorflow.keras import layers, models, applications, Input, Model
from tensorflow.keras.layers import Convolution2D, MaxPooling2D, UpSampling2D, Masking, BatchNormalization
from tensorflow.keras.layers import LSTM, Input, Concatenate, Permute, Dropout, AveragePooling2D, MaxPool2D, LeakyReLU, \
    Reshape, Conv2D, Flatten, Dense, Conv1D, GlobalMaxPooling1D, GlobalAveragePooling1D, AveragePooling1D, \
    BatchNormalization
from tensorflow.keras.layers import Input, Softmax, Masking, Embedding, Concatenate, Reshape, BatchNormalization

from sklearn.utils import shuffle

# from util.FeatureExtractionFunctions import add_key

mask_value = 0.0


def contrastive_loss(x1, x2, label, eps=1e-06, margin=1.0):
    # Compute pairwise distances between x1 and x2
    dist = tf.norm(x1 - x2 + eps, axis=-1)  # This uses the Euclidean distance (p=2)

    # Compute the contrastive loss
    loss = (1 - label) * tf.square(dist) + label * tf.square(tf.maximum(margin - dist, 0.0))

    # Return the mean of the loss
    loss = tf.reduce_mean(loss)
    return loss


def embedding_model(ft_counts, encoding_size=128, mask_value=0.0, nhead=4):
    # Input + Preproc
    inp = Input(shape=ft_counts)
    # z = Masking(mask_value=0.0)(inp)
    z = BatchNormalization()(inp)

    # Inner Part
    a = LSTM(units=128, recurrent_dropout=0.2, return_sequences=True)(z)
    a = Dropout(0.5)(a)

    a = layers.MultiHeadAttention(key_dim=64, num_heads=nhead, dropout=0.5)(a, a)
    a = ReLU()(a)
    a = GlobalMaxPooling1D()(a)
    a = Dense(int(encoding_size))(a)

    c = a
    c = Softmax(axis=1)(c)
    embedding_model = Model(inputs=inp, outputs=c)

    embedding_model.summary()

    return embedding_model


def classification_model(encoding_size=128, encoding_count=2):
    inp = Input(shape=(encoding_size, encoding_count))
    x = BatchNormalization()(inp)

    # Conv Part
    a = Conv1D(32, kernel_size=5, strides=1, padding='same')(x)
    a = ReLU()(a)
    a = AveragePooling1D(4)(a)
    a = Conv1D(32, kernel_size=5, strides=1, padding='same')(a)
    a = ReLU()(a)
    a = AveragePooling1D(2)(a)

    b = Flatten()(a)
    b = Dense(128)(b)
    a = ReLU()(a)
    a = Dropout(0.3)(a)
    b = Dense(64)(b)
    a = ReLU()(a)
    a = Dropout(0.3)(a)
    b = Dense(32)(b)
    a = ReLU()(a)
    a = Dropout(0.3)(a)

    c = Dense(1)(b)

    cm = Model(inputs=inp, outputs=c)

    return cm


class ContrastiveLossGenerator:
    def __init__(self, data, batch_size, batches, shuffle=True, mask_value=0.0):
        self.grid_mx = 10 ** 9

        self.B = batches
        self.data = data
        self.tasks = list(data.keys())

        self.batch_size = batch_size
        self.shuffle = shuffle

        self.norm_size(mask_value)
        self.generate_iteration()

    def norm_size(self, mask_value):
        mx_size = 0
        for task in self.data:
            for user in self.data[task]:
                for sess in self.data[task][user]:
                    for seg in sess:
                        mx_size = max([mx_size, seg.shape[0]])

        for task in self.data:
            for user in self.data[task]:
                for sess in self.data[task][user]:
                    for iseg in range(0, len(sess)):
                        sess[iseg] = np.pad(sess[iseg], [(0, mx_size - sess[iseg].shape[0]), (0, 0)], mode="constant",
                                            constant_values=(mask_value, mask_value))

    def generate_iteration(self):
        X1 = []
        X2 = []
        y = []

        for a in range(0, self.B):
            for b in range(0, self.batch_size):
                # collect one user randomly
                label = random.choice([0, 1])
                task = random.choice(self.tasks)
                tskusers = list(self.data[task].keys())

                user = random.choice(tskusers)
                refsess = random.randrange(0, len(self.data[task][user]))
                ref = random.choice(self.data[task][user][refsess])

                if label == 0:
                    diffsess = random.randrange(0, len(self.data[task][user]))
                    while diffsess == refsess:
                        diffsess = random.randrange(0, len(self.data[task][user]))
                    chc = random.choice(self.data[task][user][diffsess])
                else:
                    ouser = random.choice(tskusers)
                    while ouser == user:
                        ouser = random.choice(tskusers)
                    chc = random.choice(random.choice(self.data[task][ouser]))

                # add same
                X1.append(ref)
                X2.append(chc)
                y.append(label)

        self.X1 = np.array(X1)
        self.X2 = np.array(X2)
        self.y = np.array(y)

        if self.shuffle:
            self.X1, self.X2, self.y = shuffle(self.X1, self.X2, self.y)

    def on_epoch_end(self):
        self.generate_iteration()

    def __getitem__(self, index):
        if index >= self.B:
            raise IndexError()

        x1 = self.X1[index * self.batch_size:(index + 1) * self.batch_size]
        x2 = self.X2[index * self.batch_size:(index + 1) * self.batch_size]
        y = self.y[index * self.batch_size:(index + 1) * self.batch_size]

        return (x1, x2), y

    def __len__(self):
        return self.B
