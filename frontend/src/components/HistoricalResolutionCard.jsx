import React from 'react';
import './HistoricalResolutionCard.css';

export default function HistoricalResolutionCard({
  historicalMatch,
  similarity,
  hasAnalyzed
}) {
  const customerMsg = historicalMatch?.customer_message || (typeof historicalMatch === 'string' ? historicalMatch : null);
  const supportReply = historicalMatch?.support_response || null;
  const numSimilarity = typeof similarity === 'number' ? similarity : 0;

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
            <p className="card-description">Top matched resolution from the historical support corpus (500 verified pairs).</p>
          </div>
        </div>

        {hasAnalyzed && (
          <div className="retrieval-stats">
            <span className="similarity-tag">Similarity: {numSimilarity.toFixed(4)}</span>
          </div>
        )}
      </div>

      <div className="card-body historical-body">
        {!hasAnalyzed ? (
          <div className="empty-historical-state">
            <p>Run analysis to retrieve similar historical customer interactions and agent resolutions.</p>
          </div>
        ) : !customerMsg ? (
          <div className="empty-historical-state not-found">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="8" y1="12" x2="16" y2="12" />
            </svg>
            <span>No suitable historical resolution found.</span>
          </div>
        ) : (
          <>
            <div className="exchange-block">
              <div className="exchange-label customer-label">
                <span className="dot dot-customer"></span>
                <span>Historical Customer Message</span>
              </div>
              <div className="exchange-bubble customer-bubble">
                "{customerMsg}"
              </div>
            </div>

            {supportReply && (
              <>
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
                    "{supportReply}"
                  </div>
                </div>
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
}
