import React from 'react';

const QualitativeReport = ({ report }) => {
  const formatReport = (report) => {
    const sections = report.split('\n\n');
    return sections.map((section, index) => {
      const lines = section.split('\n');
      const title = lines[0];
      const content = lines.slice(1);

      return (
        <div key={index} className="report-section">
          <h3>{title}</h3>
          {content.map((line, lineIndex) => {
            if (line.startsWith('**')) {
              const [key, value] = line.split(':**');
              return (
                <p key={lineIndex} className="report-item">
                  <strong>{key.replace('**', '')}:</strong> {value.trim()}
                </p>
              );
            } else if (line.startsWith('- ')) {
              return <li key={lineIndex}>{line.slice(2)}</li>;
            } else {
              return <p key={lineIndex}>{line}</p>;
            }
          })}
        </div>
      );
    });
  };

  return <div className="report">{formatReport(report)}</div>;
};

export default QualitativeReport;