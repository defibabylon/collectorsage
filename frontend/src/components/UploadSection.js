import React, { useState, useRef } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://collectorsage-backend.onrender.com';

function UploadSection({ setComicDetails, setReport, setUploadedImage }) {
  const [image, setImage] = useState(null);
  const [status, setStatus] = useState('');
  const [processingInfo, setProcessingInfo] = useState(null);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleImageUpload = (file) => {
    setImage(file);
    setStatus('');
    setProcessingInfo(null);

    // Create a URL for the uploaded image and pass it to parent
    if (setUploadedImage) {
      const imageUrl = URL.createObjectURL(file);
      setUploadedImage(imageUrl);
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files[0]) {
      handleImageUpload(e.target.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragOver(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragOver(false);
    const files = e.dataTransfer.files;
    if (files[0] && files[0].type.startsWith('image/')) {
      handleImageUpload(files[0]);
    }
  };

  const handleZoneClick = () => {
    fileInputRef.current?.click();
  };

  const processImage = async () => {
    if (!image) {
      setStatus('Please select an image first.');
      return;
    }
    setStatus('Processing image...');
    const formData = new FormData();
    formData.append('image', image);

    try {
      const response = await axios.post(`${API_URL}/process_image`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      console.log('Response:', response.data);
      if (response.data.error) {
        setStatus('Error processing image: ' + response.data.error);
      } else {
        setComicDetails(response.data.comicDetails);
        setReport(response.data.report);

        // Store processing information
        const processingMethod = response.data.processingMethod || 'unknown';
        const processingTime = response.data.processingTime || 'N/A';
        const breakdown = response.data.breakdown || {};

        setProcessingInfo({
          method: processingMethod,
          time: processingTime,
          breakdown: breakdown
        });

        const methodText = processingMethod === 'fast' ? '⚡ Fast Processing' : '🔍 Regular Processing';
        setStatus(`✅ Processing complete using ${methodText} (${processingTime})`);
      }
    } catch (error) {
      setStatus('Error processing image');
      console.error('Error:', error);
      if (error.response) {
        console.error('Response data:', error.response.data);
        console.error('Response status:', error.response.status);
        console.error('Response headers:', error.response.headers);
      } else if (error.request) {
        console.error('Request data:', error.request);
      } else {
        console.error('Error message:', error.message);
      }
    }
  };

  return (
    <div className="upload-section">
      <div
        className={`upload-zone ${isDragOver ? 'dragover' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={handleZoneClick}
      >
        <div className="upload-icon">🖼️</div>
        <div className="upload-text">
          {image ? image.name : 'Drop your comic image here'}
        </div>
        <div className="upload-subtext">
          {image ? 'Click to change image' : 'or click to browse'}
        </div>
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileInputChange}
          accept="image/*"
        />
      </div>

      <button
        className="analyze-button"
        onClick={processImage}
        disabled={!image}
      >
        ANALYZE
      </button>

      {status && <p className="status-message">{status}</p>}

      {processingInfo && (
        <div className="processing-info">
          <div><strong>Processing Method:</strong> {processingInfo.method === 'fast' ? '⚡ Fast (Claude Only)' : '🔍 Regular (Google Vision + Claude)'}</div>
          <div><strong>Total Time:</strong> {processingInfo.time}</div>
          {processingInfo.breakdown && (
            <div style={{ marginTop: '8px' }}>
              <strong>Breakdown:</strong>
              <ul>
                {processingInfo.breakdown.image_processing && <li>Image Processing: {processingInfo.breakdown.image_processing}</li>}
                {processingInfo.breakdown.database_fetch && <li>Database Fetch: {processingInfo.breakdown.database_fetch}</li>}
                {processingInfo.breakdown.ebay_fetch && <li>eBay Fetch: {processingInfo.breakdown.ebay_fetch}</li>}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default UploadSection;
