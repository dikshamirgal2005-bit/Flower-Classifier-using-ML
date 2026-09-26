import React from "react";

const FLOWER_EMOJI = {
  daisy: "🌼",
  dandelion: "🌾",
  roses: "🌹",
  sunflowers: "🌻",
  tulips: "🌷",
};

// Reference/typical measurements per species (not measured from the photo —
// a single 2D image has no fixed scale to measure real-world size from).
const FLOWER_MEASUREMENTS = {
  daisy: { bloomDiameter: "2 – 5 cm", height: "15 – 30 cm", petals: "~20–30 petals" },
  dandelion: { bloomDiameter: "2 – 4 cm", height: "10 – 40 cm", petals: "150+ petals" },
  roses: { bloomDiameter: "4 – 12 cm", height: "30 – 200 cm", petals: "20–40 petals" },
  sunflowers: { bloomDiameter: "10 – 30 cm", height: "150 – 300 cm", petals: "~30–50 petals" },
  tulips: { bloomDiameter: "5 – 8 cm", height: "20 – 60 cm", petals: "6 petals" },
};

export default function PredictionResult({ result }) {
  if (!result) return null;

  if (result.error) {
    return <div className="result-box error">{result.error}</div>;
  }

  const emoji = FLOWER_EMOJI[result.predicted_class] || "🌸";
  const measurements = FLOWER_MEASUREMENTS[result.predicted_class];

  return (
    <div className="result-box">
      <div className="result-headline">
        <span className="result-emoji">{emoji}</span>
        <div>
          <h2>{capitalize(result.predicted_class)}</h2>
          <p className="confidence">
            {(result.confidence * 100).toFixed(1)}% confident
          </p>
        </div>
      </div>

      {measurements && (
        <div className="measurements">
          <p className="measurements-title">
            Typical measurements for this species
          </p>
          <div className="measurements-grid">
            <div className="measurement-item">
              <span className="measurement-icon">📏</span>
              <span className="measurement-label">Bloom diameter</span>
              <span className="measurement-value">
                {measurements.bloomDiameter}
              </span>
            </div>
            <div className="measurement-item">
              <span className="measurement-icon">🌱</span>
              <span className="measurement-label">Plant height</span>
              <span className="measurement-value">{measurements.height}</span>
            </div>
            <div className="measurement-item">
              <span className="measurement-icon">🌸</span>
              <span className="measurement-label">Petal count</span>
              <span className="measurement-value">{measurements.petals}</span>
            </div>
          </div>
          <p className="measurements-note">
            Reference ranges for a typical {result.predicted_class.replace(/s$/, "")},
            not measured from your photo.
          </p>
        </div>
      )}

      <div className="all-predictions">
        {result.all_predictions.map((p) => (
          <div className="prediction-row" key={p.class}>
            <span className="prediction-label">{capitalize(p.class)}</span>
            <div className="prediction-bar-track">
              <div
                className="prediction-bar-fill"
                style={{ width: `${p.confidence * 100}%` }}
              />
            </div>
            <span className="prediction-pct">
              {(p.confidence * 100).toFixed(1)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}
