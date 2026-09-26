import React, { useState } from "react";
import "./App.css";
import ImageUpload from "./components/ImageUpload";
import PredictionResult from "./components/PredictionResult";

// Change this if your Flask backend runs on a different host/port
const API_URL = "http://localhost:5000/api/predict";

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleImageSelected = (file) => {
    setSelectedFile(file);
    setPreviewUrl(URL.createObjectURL(file));
    setResult(null);
  };

  const handlePredict = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("image", selectedFile);

      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });
      const data = await response.json();

      if (!response.ok) {
        setResult({ error: data.error || "Something went wrong." });
      } else {
        setResult(data);
      }
    } catch (err) {
      setResult({
        error:
          "Could not reach the prediction server. Is the Flask backend running on port 5000?",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreviewUrl(null);
    setResult(null);
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🌷 Flower Classifier</h1>
        <p>Upload a photo of a flower and let the model guess its species.</p>
      </header>

      <main className="app-main">
        <ImageUpload
          onImageSelected={handleImageSelected}
          previewUrl={previewUrl}
        />

        <div className="button-row">
          <button
            className="predict-btn"
            onClick={handlePredict}
            disabled={!selectedFile || loading}
          >
            {loading ? "Predicting..." : "Predict Flower"}
          </button>
          {selectedFile && (
            <button className="reset-btn" onClick={handleReset}>
              Reset
            </button>
          )}
        </div>

        <PredictionResult result={result} />
      </main>

      <footer className="app-footer">
        <p>Model: MobileNetV2 transfer learning · Dataset: tf_flowers (5 classes)</p>
      </footer>
    </div>
  );
}
