"""
Flower Classification - Backend API
------------------------------------
Loads the trained Keras model (flower_model.h5) and exposes a
POST /api/predict endpoint that accepts an uploaded image and
returns the predicted flower class with a confidence score.

Run:
    pip install -r requirements.txt
    python app.py

Make sure flower_model.h5 and class_names.json (produced by
model_training/train_model.py) are placed in this same folder
before starting the server.
"""

import io
import json
import os

import numpy as np
from flask import Flask, jsonify, request
from flask_cors import CORS
from PIL import Image
import tensorflow as tf

APP_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(APP_DIR, "flower_model.h5")
CLASSES_PATH = os.path.join(APP_DIR, "class_names.json")
IMG_SIZE = 160

app = Flask(__name__)
CORS(app)  # allow requests from the React dev server (localhost:3000)

model = None
class_names = []


def load_artifacts():
    global model, class_names
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Could not find {MODEL_PATH}. Train the model first with "
            "model_training/train_model.py and copy flower_model.h5 + "
            "class_names.json into the backend/ folder."
        )
    model = tf.keras.models.load_model(MODEL_PATH)
    with open(CLASSES_PATH) as f:
        class_names = json.load(f)
    print(f"Loaded model. Classes: {class_names}")


def preprocess_image(file_bytes):
    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    image = image.resize((IMG_SIZE, IMG_SIZE))
    array = np.array(image, dtype=np.float32)
    array = tf.keras.applications.mobilenet_v2.preprocess_input(array)
    return np.expand_dims(array, axis=0)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model_loaded": model is not None})


@app.route("/api/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided. Send it as form-data field 'image'."}), 400

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "Empty filename."}), 400

    try:
        file_bytes = file.read()
        batch = preprocess_image(file_bytes)
        predictions = model.predict(batch)[0]

        top_index = int(np.argmax(predictions))
        result = {
            "predicted_class": class_names[top_index],
            "confidence": float(predictions[top_index]),
            "all_predictions": [
                {"class": class_names[i], "confidence": float(predictions[i])}
                for i in range(len(class_names))
            ],
        }
        result["all_predictions"].sort(key=lambda x: x["confidence"], reverse=True)
        return jsonify(result)

    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    load_artifacts()
    app.run(debug=True, host="0.0.0.0", port=5000)
