import cv2
import keras
import numpy as np
import tensorflow as tf

from config import get_config

config = get_config()
model_file = config.models_dir / "CNN_best_model.keras"
model: keras.models.Model = tf.keras.models.load_model(model_file)  # type: ignore


# def preprocess_image(image: np.ndarray) -> np.ndarray:
#     image = cv2.resize(image, (224, 224))
#     image = image.reshape(1, 224, 224, 3)
#     # image = np.divide(image, 255.0)
#     return image


def prepare_image(img: np.ndarray) -> np.ndarray:
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (224, 224))
    img = np.expand_dims(img, axis=0)
    img = np.divide(img, 255.0)
    return img


def predict(image: np.ndarray) -> float:
    image = prepare_image(image)
    prediction = model.predict(image)
    print(prediction)
    return prediction.item()
