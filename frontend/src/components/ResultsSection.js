import React from 'react';
import QualitativeReport from './QualitativeReport';

const ResultsSection = ({ comicDetails, report }) => {
  return (
    <div className="results-section">
      {comicDetails && (
        <div className="comic-details">
          <h2>Comic Details</h2>
          <p><strong>Title:</strong> {comicDetails.title}</p>
          <p><strong>Issue Number:</strong> {comicDetails.issueNumber}</p>
          <p><strong>Year:</strong> {comicDetails.year}</p>
        </div>
      )}
      {report && (
        <div className="qualitative-report">
          <h2>Qualitative Report</h2>
          <QualitativeReport report={report} />
        </div>
      )}
    </div>
  );
};

export default ResultsSection;