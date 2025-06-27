import React, { useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://collectorsage-backend.onrender.com';

function UploadSection({ setComicDetails, setReport }) {
  const [image, setImage] = useState(null);
  const [status, setStatus] = useState('');
  const [processingInfo, setProcessingInfo] = useState(null);

  const handleImageUpload = (e) => {
    setImage(e.target.files[0]);
    setStatus('');
    setProcessingInfo(null);
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
      <h2>Upload Comic Book Image</h2>
      <input type="file" onChange={handleImageUpload} accept="image/*" />
      <button onClick={processImage}>Process Image</button>
      {status && <p className="status-message">{status}</p>}

      {processingInfo && (
        <div className="processing-info" style={{
          marginTop: '10px',
          padding: '10px',
          backgroundColor: '#f0f8ff',
          borderRadius: '5px',
          fontSize: '14px'
        }}>
          <div><strong>Processing Method:</strong> {processingInfo.method === 'fast' ? '⚡ Fast (Claude Only)' : '🔍 Regular (Google Vision + Claude)'}</div>
          <div><strong>Total Time:</strong> {processingInfo.time}</div>
          {processingInfo.breakdown && (
            <div style={{ marginTop: '5px' }}>
              <strong>Breakdown:</strong>
              <ul style={{ margin: '5px 0', paddingLeft: '20px' }}>
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
