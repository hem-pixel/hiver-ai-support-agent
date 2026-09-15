import React from 'react';
import './HistoricalResolutionCard.css';

export default function HistoricalResolutionCard({
  historicalCustomer = "@115873 I got charged twice for one ride I'm trying to get a refund can you help me",
  historicalSupport = "@438093 We can take a look! Send us a note via https://t.co/zJ6aIZinzb so our team can get in touch.",
  similarity = 0.7533,
  intent = "fare_or_charge_issue"
}) {
  return (
    <div className="card historical-resolution-card">
      <div className="card-header">
        <div className="card-header-left">
          <div className="card-icon-badge historical-icon">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
              <polyline points="14 2 14 8 20 8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10 9 9 9 8 9" />
            </svg>
          </div>
          <div>
            <h2 className="card-title">Retrieved Historical Resolution</h2>
            <p className="card-description">Top matched resolution from the historical support corpus (500+ verified cases).</p>
          </div>
        </div>

        <div className="retrieval-stats">
          <span className="similarity-tag">Similarity: {similarity.toFixed(4)}</span>
        </div>
      </div>

      <div className="card-body historical-body">
        <div className="exchange-block">
          <div className="exchange-label customer-label">
            <span className="dot dot-customer"></span>
            <span>Historical Customer Message</span>
          </div>
          <div className="exchange-bubble customer-bubble">
            "{historicalCustomer}"
          </div>
        </div>

        <div className="exchange-divider">
          <div className="divider-line"></div>
          <span className="divider-icon">↓</span>
          <div className="divider-line"></div>
        </div>

        <div className="exchange-block">
          <div className="exchange-label support-label">
            <span className="dot dot-support"></span>
            <span>Historical Uber Support Agent Response</span>
          </div>
          <div className="exchange-bubble support-bubble">
            "{historicalSupport}"
          </div>
        </div>
      </div>
    </div>
  );
}
