import React, { useRef, useState } from "react";

export default function ImageUpload({ onImageSelected, previewUrl }) {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef(null);

  const handleFile = (file) => {
    if (file && file.type.startsWith("image/")) {
      onImageSelected(file);
    }
  };

  return (
    <div
      className={`upload-box ${isDragging ? "dragging" : ""}`}
      onClick={() => inputRef.current.click()}
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={(e) => {
        e.preventDefault();
        setIsDragging(false);
        handleFile(e.dataTransfer.files[0]);
      }}
    >
      <input
        type="file"
        accept="image/*"
        ref={inputRef}
        style={{ display: "none" }}
        onChange={(e) => handleFile(e.target.files[0])}
      />
      {previewUrl ? (
        <img src={previewUrl} alt="Selected flower" className="preview-img" />
      ) : (
        <div className="upload-placeholder">
          <span className="upload-icon">🌸</span>
          <p>Click or drag a flower photo here</p>
          <p className="upload-hint">JPG or PNG</p>
        </div>
      )}
    </div>
  );
}
