import React from 'react';
import QualitativeReport from './QualitativeReport';

const ResultsSection = ({ comicDetails, report, uploadedImage }) => {
  if (!comicDetails && !report) {
    return null;
  }

  return (
    <div className="results-section">
      {comicDetails && (
        <div className="results-card">
          <div className="comic-details">
            {uploadedImage && (
              <img
                src={uploadedImage}
                alt="Comic Cover"
                className="comic-cover"
              />
            )}
            <div className="comic-info">
              <h2>{comicDetails.title}</h2>
              <div className="comic-meta">#{comicDetails.issueNumber}, {comicDetails.year}</div>
            </div>
          </div>
        </div>
      )}

      {report && (
        <div className="results-card">
          <h2 style={{ color: '#1a237e', marginBottom: '20px' }}>Detailed Report</h2>
          <QualitativeReport report={report} />
        </div>
      )}
    </div>
  );
};

export default ResultsSection;