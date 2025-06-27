import React, { useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'https://collectorsage-backend.onrender.com';

function UploadSection({ setComicDetails, setReport }) {
  const [image, setImage] = useState(null);
  const [status, setStatus] = useState('');

  const handleImageUpload = (e) => {
    setImage(e.target.files[0]);
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
        setStatus('Processing complete');
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
    </div>
  );
}

export default UploadSection;
