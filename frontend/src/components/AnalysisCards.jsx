import React from 'react';
import './AnalysisCards.css';

export default function AnalysisCards({
  intent,
  confidence,
  similarity,
  hasAnalyzed
}) {
  const formatIntentLabel = (slug) => {
    if (!slug) return "Awaiting input...";
    return slug
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const hasConfidence = confidence !== null && confidence !== undefined;
  const confidencePercent = hasConfidence ? Math.round(confidence * 100) : null;
  const numSimilarity = typeof similarity === 'number' ? similarity : 0;
  const similarityPercent = Math.round(numSimilarity * 100);

  return (
    <div className="analysis-grid">
      {/* 1. Predicted Intent Card */}
      <div className="card metric-card">
        <div className="metric-header">
          <span className="metric-title">Predicted Intent</span>
          <span className="metric-badge-tag">Classification</span>
        </div>
        <div className="metric-content">
          <div className="intent-display">
            <span className="intent-chip">
              {hasAnalyzed ? formatIntentLabel(intent) : "Awaiting analysis"}
            </span>
            {intent && <code className="intent-slug">{intent}</code>}
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
          <span className="metric-badge-tag">Probability</span>
        </div>
        <div className="metric-content">
          {hasConfidence ? (
            <>
              <div className="metric-value-row">
                <span className="metric-number">{confidencePercent}%</span>
                <span className="metric-qualifier high">Calibrated</span>
              </div>
              <div className="progress-bar-bg">
                <div
                  className="progress-bar-fill primary"
                  style={{ width: `${confidencePercent}%` }}
                ></div>
              </div>
            </>
          ) : (
            <div className="metric-value-row uncalibrated">
              <span className="metric-number muted-text">Not available</span>
              <span className="metric-qualifier neutral">Rule-based model</span>
            </div>
          )}
        </div>
        <div className="metric-footer">
          <span>
            {hasConfidence
              ? "Model calibrated score"
              : "Rule baseline does not output confidence"}
          </span>
        </div>
      </div>

      {/* 3. Historical Similarity Card */}
      <div className="card metric-card">
        <div className="metric-header">
          <span className="metric-title">Historical Similarity</span>
          <span className="metric-badge-tag">TF-IDF Metric</span>
        </div>
        <div className="metric-content">
          {hasAnalyzed ? (
            <>
              <div className="metric-value-row">
                <span className="metric-number">{numSimilarity.toFixed(4)}</span>
                <span className={`metric-qualifier ${numSimilarity >= 0.20 ? 'high' : 'low'}`}>
                  {numSimilarity >= 0.20 ? 'Strong Match' : 'Weak Match'}
                </span>
              </div>
              <div className="progress-bar-bg">
                <div
                  className="progress-bar-fill accent"
                  style={{ width: `${Math.min(similarityPercent * 1.2, 100)}%` }}
                ></div>
              </div>
            </>
          ) : (
            <div className="metric-value-row uncalibrated">
              <span className="metric-number muted-text">—</span>
              <span className="metric-qualifier neutral">Awaiting analysis</span>
            </div>
          )}
        </div>
        <div className="metric-footer">
          <span>Threshold cutoff: &gt;= 0.20</span>
        </div>
      </div>
    </div>
  );
}
