import React from 'react';
import './AnalysisCards.css';

export default function AnalysisCards({
  intent = "fare_or_charge_issue",
  confidence = 0.92,
  similarity = 0.7533
}) {
  const formatIntentLabel = (slug) => {
    if (!slug) return "None";
    return slug
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const confidencePercent = Math.round(confidence * 100);
  const similarityPercent = Math.round(similarity * 100);

  return (
    <div className="analysis-grid">
      {/* 1. Predicted Intent Card */}
      <div className="card metric-card">
        <div className="metric-header">
          <span className="metric-title">Predicted Intent</span>
          <span className="metric-badge-tag">AI Classification</span>
        </div>
        <div className="metric-content">
          <div className="intent-display">
            <span className="intent-chip">{formatIntentLabel(intent)}</span>
            <code className="intent-slug">{intent}</code>
          </div>
        </div>
        <div className="metric-footer">
          <span>Uber Support 10-Intent Taxonomy</span>
        </div>
      </div>

      {/* 2. Confidence Card */}
      <div className="card metric-card">
        <div className="metric-header">
          <span className="metric-title">Classification Confidence</span>
          <span className="metric-badge-tag">Score</span>
        </div>
        <div className="metric-content">
          <div className="metric-value-row">
            <span className="metric-number">{confidencePercent}%</span>
            <span className="metric-qualifier high">High Confidence</span>
          </div>
          <div className="progress-bar-bg">
            <div
              className="progress-bar-fill primary"
              style={{ width: `${confidencePercent}%` }}
            ></div>
          </div>
        </div>
        <div className="metric-footer">
          <span>Weighted rule & keyword signal</span>
        </div>
      </div>

      {/* 3. Historical Similarity Card */}
      <div className="card metric-card">
        <div className="metric-header">
          <span className="metric-title">Historical Similarity</span>
          <span className="metric-badge-tag">TF-IDF Vector</span>
        </div>
        <div className="metric-content">
          <div className="metric-value-row">
            <span className="metric-number">{similarity.toFixed(4)}</span>
            <span className={`metric-qualifier ${similarity >= 0.20 ? 'high' : 'low'}`}>
              {similarity >= 0.20 ? 'Strong Match' : 'Weak Match'}
            </span>
          </div>
          <div className="progress-bar-bg">
            <div
              className="progress-bar-fill accent"
              style={{ width: `${Math.min(similarityPercent * 1.2, 100)}%` }}
            ></div>
          </div>
        </div>
        <div className="metric-footer">
          <span>Threshold cutoff: &gt;= 0.20</span>
        </div>
      </div>
    </div>
  );
}
