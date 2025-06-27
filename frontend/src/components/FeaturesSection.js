import React from 'react';

const FeaturesSection = () => {
  const features = [
    {
      icon: '🤖',
      title: 'AI Image Recognition',
      description: 'Identify comics using advanced AI algorithms'
    },
    {
      icon: '🏪',
      title: 'Real-time eBay Data',
      description: 'Fetch pricing information from eBay listings'
    },
    {
      icon: '📚',
      title: 'Database Comparison',
      description: 'Cross check against our extensive comic database'
    },
    {
      icon: '👨‍💼',
      title: 'Expert Analysis',
      description: 'Leverage insights from experienced comic appraisers'
    }
  ];

  return (
    <div className="features-section">
      <div className="features-grid">
        {features.map((feature, index) => (
          <div key={index} className="feature-card">
            <div className="feature-icon">{feature.icon}</div>
            <h3 className="feature-title">{feature.title}</h3>
            <p className="feature-description">{feature.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FeaturesSection;
