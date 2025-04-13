import os

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.model_selection import train_test_split
import logging

from src.preprocess import CATEGORY_NAMES
from src.preprocess import MAX_CATEGORY_INDEX


def quantile_loss(q):
    def loss(y_true, y_pred):
        e = y_true - y_pred
        return tf.reduce_mean(tf.maximum(q * e, (q - 1) * e), axis=-1)

    return loss


class Model():
    def __init__(self):
        self.models = {}
        self.categories = list(CATEGORY_NAMES.values())

    def create_single_model(self, input_size=3):
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(input_size,)),
            tf.keras.layers.Dense(256, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01)),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(128, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01)),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01)),
            tf.keras.layers.Dropout(0.3),
            tf.keras.layers.Dense(32, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.01)),
            tf.keras.layers.Dense(1, activation='linear'),
        ])
        model.compile(optimizer='adam', loss=quantile_loss(0.75), metrics=['mae'])
        return model

    def create(self, input_size=3):
        for cat_idx in range(MAX_CATEGORY_INDEX + 1):
            self.models[cat_idx] = self.create_single_model(input_size)
        return self.models

    def train(self, epochs=20, dataset_path='data/users_processed.csv'):
        df = pd.read_csv(dataset_path)
        base_features = ['gender', 'age', 'monthly_income_amt']

        for cat in range(MAX_CATEGORY_INDEX + 1):
            cat_name = CATEGORY_NAMES[cat]
            if cat_name not in df.columns:
                continue

            print(f"Обучение модели для категории: {cat_name}")

            X = df[base_features].values.astype(float)
            y = df[cat_name].values.reshape(-1, 1)

            X[:, 1] /= 80
            X[:, 2] /= 3000

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

            early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
            reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=3, verbose=0)

            self.models[cat].fit(
                X_train, y_train,
                validation_data=(X_test, y_test),
                epochs=epochs,
                batch_size=32,
                callbacks=[early_stopping, reduce_lr],
                verbose=0
            )

            eval_loss = self.models[cat].evaluate(X_test, y_test, verbose=0)
            print(f"  MAE для категории {cat_name}: {int(eval_loss[1])}")

    def predict(self, input_data):
        gender, age, income = input_data[0]

        norm_input = np.array([[gender, age / 80, income / 3000]], dtype=float)

        all_predictions = []
        for cat in range(MAX_CATEGORY_INDEX + 1):
            if cat in self.models:
                prediction = self.models[cat].predict(norm_input, verbose=0)
                if prediction[0][0] < 0:
                    all_predictions.append(0)
                else:
                    all_predictions.append(prediction[0][0])
            else:
                all_predictions.append(0)

        return [all_predictions]

    def save(self, path_prefix='model'):
        for cat_idx, model in self.models.items():
            model.save(f"models/{path_prefix}_cat_{cat_idx}.h5")

    def load(self, path_prefix='model'):
        for cat in range(MAX_CATEGORY_INDEX + 1):
            print(cat)
            model_path = f"models/{path_prefix}_cat_{cat}.h5"
            if os.path.exists(model_path):
                try:
                    loaded_model = tf.keras.models.load_model(
                        model_path,
                        custom_objects={"quantile_loss": quantile_loss(0.75)},
                        compile=False
                    )
                    self.models[cat] = loaded_model
                except Exception as e:
                    print(f"Не удалось загрузить модель для категории {cat}: {e}")
            else:
                print(f"Модель для категории {cat} не найдена по пути {model_path}.")
