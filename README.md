# 🌷 Flower Classification Project

An end-to-end flower classification project:
1. **model_training/** – trains an image classifier (transfer learning on MobileNetV2) on the public `tf_flowers` dataset (daisy, dandelion, rose, sunflower, tulip).
2. **backend/** – a Flask API that loads the trained model and serves predictions.
3. **frontend/** – a React app where a user uploads a flower photo and sees the predicted species with a confidence score.

```
flower-classification/
├── model_training/
│   ├── train_model.py
│   └── requirements.txt
├── backend/
│   ├── app.py
│   └── requirements.txt
└── frontend/
    ├── package.json
    ├── public/index.html
    └── src/
        ├── App.js
        ├── App.css
        ├── index.js
        ├── index.css
        └── components/
            ├── ImageUpload.js
            └── PredictionResult.js
```

## 1. Train the model

```bash
cd model_training
python -m venv venv && source venv/bin/activate   # optional but recommended
pip install -r requirements.txt
python train_model.py
```

This downloads the `tf_flowers` dataset automatically (needs internet access the
first time), trains a MobileNetV2-based classifier, and produces two files:

- `flower_model.h5` – the trained model
- `class_names.json` – the list of class labels

Training takes a few minutes on CPU, faster with a GPU.

**Copy both files into the `backend/` folder** once training finishes:

```bash
cp flower_model.h5 class_names.json ../backend/
```

## 2. Run the backend API

```bash
cd backend
python -m venv venv && source venv/bin/activate   # optional
pip install -r requirements.txt
python app.py
```

The API starts on `http://localhost:5000` with two endpoints:
- `GET  /api/health` – check the server and model are up
- `POST /api/predict` – send a form-data field named `image`, get back the
  predicted flower class + confidence scores for every class

## 3. Run the React frontend

```bash
cd frontend
npm install
npm start
```

This opens `http://localhost:3000`. Upload or drag a flower photo, click
**Predict Flower**, and the app calls the Flask API and shows the result with
the image and a confidence breakdown for each class.

> The frontend is pre-configured to call the backend at
> `http://localhost:5000/api/predict`. If you deploy the backend elsewhere,
> update `API_URL` at the top of `frontend/src/App.js`.

## Notes

- The 5 flower classes are exactly what `tf_flowers` provides: **daisy,
  dandelion, roses, sunflowers, tulips**. If you want different flower
  species, replace the dataset-loading part of `train_model.py` with your
  own labeled image folders (e.g. using
  `tf.keras.utils.image_dataset_from_directory`).
- CORS is already enabled on the Flask side (`flask-cors`) so the React dev
  server can call it directly during development.
- For production, build the React app (`npm run build`) and serve the static
  files from any static host, and deploy the Flask API behind a proper WSGI
  server (e.g. gunicorn) instead of the built-in dev server.
