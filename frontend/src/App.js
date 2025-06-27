import React, { useState } from 'react';
import './App.css';
import UploadSection from './components/UploadSection';
import ResultsSection from './components/ResultsSection';
import FeaturesSection from './components/FeaturesSection';

function App() {
  const [comicDetails, setComicDetails] = useState(null);
  const [report, setReport] = useState('');
  const [uploadedImage, setUploadedImage] = useState(null);

  return (
    <div className="container">
      <header className="app-header">
        <h1>COLLECTORSAGE</h1>
        <p className="tagline">AI-POWERED COMIC BOOK VALUATION</p>
      </header>

      <UploadSection
        setComicDetails={setComicDetails}
        setReport={setReport}
        setUploadedImage={setUploadedImage}
      />

      <FeaturesSection />

      <ResultsSection
        comicDetails={comicDetails}
        report={report}
        uploadedImage={uploadedImage}
      />
    </div>
  );
}

export default App;
