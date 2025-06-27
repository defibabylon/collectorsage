import React, { useState } from 'react';
import './App.css';
import UploadSection from './components/UploadSection';
import ResultsSection from './components/ResultsSection';

function App() {
  const [comicDetails, setComicDetails] = useState(null);
  const [report, setReport] = useState('');

  return (
    <div className="container">
      <header className="app-header">
        <h1>Comic Book Price Analyzer</h1>
      </header>
      <UploadSection setComicDetails={setComicDetails} setReport={setReport} />
      <ResultsSection comicDetails={comicDetails} report={report} />
    </div>
  );
}

export default App;
